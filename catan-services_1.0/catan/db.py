"""
    This file contains all of CATAN database operations
    
    @author: Chad Spensky
    © 2015 Massachusetts Institute of Technology
"""

import os
import logging
logger = logging.getLogger(__name__)
import sqlite3
import inspect
import json
import time
import re
import base64
import struct
import socket
import SocketServer
import multiprocessing
from multiprocessing import Process, Lock

# CATAN
from data import NodeMessage
from catan.comms import TxClient, TxServer
import catan.globals as G
import catan.metrics

db_mutex = Lock()

class DBSchema:
    """
        This is our default database schema class
    """
    def _get_sql_insert(self, **kargs):
        
        keys = []
        values = []
        value_list = []
        
        for k, v in kargs.items():
            # Escape quotes
            k = str(k).replace("'","''")
#             v = str(v).replace("'","''")
            
            # Append our strings
            keys.append(k)
            values.append("?")
            value_list.append(v)
            
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            
            # Skip None values
            if v is None:
                continue
            
            # Escape quotes
            k = str(k).replace("'","'")
#             v = str(v).replace("'","''")
            
            # Append our strings
            keys.append(k)
            values.append("?")
            value_list.append(v)

        keys = "(" + ",".join(keys) + ")"
        values = "(" + ",".join(values) + ")"
        
        # Return SQL string
        return ("INSERT INTO %s %s VALUES %s"%(
                                               self.__class__.__name__,
                                               keys,
                                               values),
                                               value_list) 


    def sql_insert(self, person_id, submission_id, origin_node_id):
        return self._get_sql_insert(person_id=person_id,
                             submission_id=submission_id,
                             origin_node_id=origin_node_id)
    
    
    def get_fields(self):
        """
            Return just our list of fields
        """
        fields = []
        for k in dir(self):
            if k.startswith("_") or callable(getattr(self,k)):
                continue
            fields.append(k)
        return fields
    
    
    def has_entries(self):
        """
            Return True if any of our fields are populated, False otherwise.
        """
        fields = self.get_fields()
        for f in fields:
            if getattr(self,f) is not None:
                return True
        return False


class db_node_info(DBSchema):
    node_id = None
    gps_latitude = None
    gps_longitude = None
    gps_altitude = None
    gps_sat_count = None
    visited = None

    def sql_insert(self, node_id, visited, timestamp):
        return self._get_sql_insert(node_id=node_id,
                                    visited=visited,
                                    timestamp=time.time())
    
    _SQL_CREATE = '''CREATE TABLE db_node_info
            (node_id int, gps_latitude real, gps_longitude real, gps_altitude real, gps_sat_count int, visited int, timestamp real)'''

class db_catan_identity(DBSchema):
    
    def sql_insert(self, person_id, submission_id,timestamp=time.time()):
        return self._get_sql_insert(person_id=person_id,
                             submission_id=submission_id,
                             timestamp=timestamp)
    
    _SQL_CREATE = '''CREATE TABLE db_catan_identity
            (person_id int, submission_id int, timestamp real)'''


class db_submitter_info(DBSchema):
    submitter_id = None
    imsi = None
    cookie = None
    gps_latitude = None
    gps_longitude = None
    gps_accuracy = None
    
    def sql_insert(self, submission_id, origin_node_id, origin_person_id, timestamp=time.time()):
        return self._get_sql_insert(submission_id=submission_id,
                                    origin_node_id=origin_node_id,
                                    submitter_id=origin_person_id,
                                    timestamp=timestamp)
        
    _SQL_CREATE = '''CREATE TABLE db_submitter_info 
        (submission_id int, origin_node_id int, 
        submitter_id int,
        imsi int, 
        cookie text, 
        gps_latitude real, 
        gps_longitude real, 
        gps_accuracy real, 
        timestamp real)'''
        
        
class db_person_bio(DBSchema):
    name_family = None
    name_given = None
    age = None
    sex = None
    
    
    _SQL_CREATE = '''CREATE TABLE db_person_bio 
        (person_id int, origin_node_id int, submission_id int, 
        name_family text, 
        name_given text, 
        age text, 
        sex text)'''
    
class db_person_description(DBSchema):
    person_description = None
    
    _SQL_CREATE = '''CREATE TABLE db_person_description
            (person_id int, origin_node_id int, submission_id int, 
            person_description text)'''
        
class db_person_contact(DBSchema):
    street = None
    neighborhood = None
    city = None
    state = None
    zip = None
    state = None
    country = None
    phone = None
    email = None
    
    _SQL_CREATE = '''CREATE TABLE db_person_contact
            (person_id int, origin_node_id int, submission_id int, 
            street text, 
            neighborhood text,
            city text,
            zip text,
            state text,
            country text,
            phone text, 
            email text)'''
    

    
class db_pictures(DBSchema):
    picture_data = None
    
    def sql_insert(self, picture_id, origin_node_id):
        keys = "(picture_id, origin_node_id, picture_data)"
        values = "('%s','%s',?)"%(picture_id, origin_node_id)
        return "INSERT INTO %s %s VALUES %s"%(self.__class__.__name__,keys,values)
    
    _SQL_CREATE = '''CREATE TABLE db_pictures
            (picture_id int, origin_node_id int,
             picture_data blob)'''
        
        
class db_person_pictures(DBSchema):
    picture_description = None
    
    def sql_insert(self, person_id, submission_id, origin_node_id, picture_id):
        return self._get_sql_insert(person_id=person_id,
                             submission_id=submission_id,
                             origin_node_id=origin_node_id,
                             picture_id=picture_id)
    
    _SQL_CREATE = '''CREATE TABLE db_person_pictures
            (person_id int, origin_node_id int, submission_id, 
            picture_id, 
            picture_description text)'''


class db_person_links(DBSchema):
    person_id2 = None
    relationship = None
    
    _SQL_CREATE = '''CREATE TABLE db_person_links
            (person_id int, origin_node_id int, submission_id int, 
            person_id2 int, 
            relationship text)'''

class db_person_messages(DBSchema):
    person_message = None
    status = None
    status_location = None
    status_gps_latitude = None
    status_gps_longitude = None
    status_gps_accuracy = None
    
    _SQL_CREATE = '''CREATE TABLE db_person_messages
            (person_id int, origin_node_id int, submission_id int,
            status text,
            status_location text,
            status_gps_latitude real,
            status_gps_longitude real,
            status_gps_accuracy real,
            person_message text)'''

class CatanDatabase:
    """
        Class to interface with our sqlite database
    """
    
    def __init__(self, node_id=-1, filename=G.DB_FILENAME):
        """
            Initilize our class and save relevant info
        """
        self.filename = filename
        self.my_node_id = node_id
        self.CONN = None
        
        self.next_person_id = None
        self.next_submission_id = None
        self.next_picture_id = None
        
        # Connect to our DB
        self._connect()
    
    
    def __create(self):
        """
            Create our database schema
        """
        
        try:
            c = self.CONN.cursor()
            
            # Tables with CATAN data
            c.execute(db_node_info._SQL_CREATE)
            
            c.execute('''CREATE TABLE catan_messages
            (message_id int, message text, timestamp real)''')
            
            c.execute(db_catan_identity._SQL_CREATE)
            
            # Table to handle all submitted data
            c.execute(db_submitter_info._SQL_CREATE)
                
            # Tables with people data
            c.execute(db_person_bio._SQL_CREATE)
            
            c.execute(db_person_description._SQL_CREATE)
            
            c.execute(db_person_contact._SQL_CREATE)
            
            c.execute(db_person_pictures._SQL_CREATE)
            
            c.execute(db_person_messages._SQL_CREATE)
            
#             c.execute(db_person_status._SQL_CREATE)
            
#             c.execute(db_person_location._SQL_CREATE)
            
            c.execute(db_person_links._SQL_CREATE)
            
            
            # Binary tables
            c.execute(db_pictures._SQL_CREATE)
            
            # Commit our queries
            self.CONN.commit()
            
        except:
            import traceback
            traceback.print_exc()
            logger.error("Could not create tables in database!")
            return False
        
        return True
    
    
    def _connect(self):
        """
            Connect to our database
        """
        logger.debug("Connecting to database at %s"%self.filename)
        if self.CONN is not None:
            return True
        
        # Does our database already exist?
        init = False
        if not os.path.exists(self.filename):
            # Create our directories
            try:
                os.makedirs(os.path.dirname(self.filename),0755)
            except:
                pass
            init = True
        
        # Connect to our DB
        try:
            self.CONN = sqlite3.connect(self.filename)
        except:
            logger.error("Could not connect to database. (%s)"%self.filename)
            self.CONN = None
            return False
            
        # Create all of our tables
        if init:
            return self.__create()
        else:
            return True


    def _sql(self, cmd, fields):
        
        self.CONN.row_factory = sqlite3.Row
        c = self.CONN.cursor()
        
        rtn = None

        if fields is not None:
            rtn = c.execute(cmd, fields)
        else:
            rtn = c.execute(cmd)

        self.CONN.commit()
        
        return rtn

    def get_person_counts_by_node(self):
        """
            Return the number of people in the database by origin node id as a dict.
        """
        
        #SQL = "SELECT ROUND(person_id*100)%100 as Node, COUNT(*) FROM db_person_bio GROUP BY Node"
        SQL = "SELECT person_id FROM db_person_bio"
        
        result = self._sql(SQL, None).fetchall()

        #get the node encoded in the decimal portion of the person_id
        nodes = [int(entry[0].split('-')[1]) for entry in result]
	#print nodes
        
        #aggregate by nodes
        node_dict = {}
        for node in nodes:
            if node in node_dict:
                node_dict[node] += 1
            else:
                node_dict[node] = 1
                
        return node_dict
        
        
    def get_recent_fields_for_person(self, database_name, person_id):
        """
            Returns a dictionary containing the most recently updated values
            in each field of the selected database for the given person_id.
            
            database_name should NOT be derived from user supplied values.
        """
        
        SQL = '''SELECT * 
                 FROM %s AS in_db 
                 JOIN db_submitter_info AS sub
                    ON sub.submission_id=in_db.submission_id
                 WHERE sub.submission_id=in_db.submission_id
                 AND sub.origin_node_id=in_db.origin_node_id 
                 AND in_db.person_id = ? 
                 ORDER BY sub.timestamp DESC'''

      	SQL = SQL % database_name

        results = self._sql(SQL, [person_id])
        
        data = results.fetchall()
        
        ret_dict = {}
        if data:
            columns = data[0].keys()
            #print columns
            for row in data:
                for key, val in zip(columns, row):
                    if key not in ret_dict:
                        ret_dict[key] = val
                        
                    if key in ret_dict and ret_dict[key] is None:
                        ret_dict[key] = val
        else:
            ret_dict = None
            
        return ret_dict
        
    
    def get_person_info(self, person_id):
        """
            Returns a dictionary containing the most recent values for all
            the fields associated with a given person id.
        """
        summary_dict = {}
        databases = ['db_person_bio', 'db_person_contact', 'db_person_description']
        for db in databases:
            temp_dict = self.get_recent_fields_for_person(db, person_id)
            if temp_dict:
                summary_dict.update(temp_dict)
        
        return summary_dict
        
    def get_person_ids(self):
        """
            Returns a list of all person_id entries in the database
        """
        SQL = '''SELECT person_id
                 FROM db_person_bio'''
                 
        results = self._sql(SQL, []).fetchall()
        
        results_list = [r[0] for r in results]
        
        return results_list
        
        
    def get_messages_by_person(self, person_id):
        """
            Returns a list of dictionaries.  Each dictionary contains the fields
            specified below describing the contents of one person message.
        """                
        #define the data items that will be retreived
        variables = ['person_id', 'origin_node_id', 'status', 'status_location', 
                     'status_gps_latitude', 'status_gps_longitude', 'status_gps_accuracy', 
                     'person_message', 'imsi', 'gps_latitude', 'gps_longitude', 'gps_accuracy', 
                     'timestamp', 'sub_name_family', 'sub_name_given', 'sub_age', 'sub_sex',
                     'submission_id']
                     
        #the selected fields should correspond (in order) the variables above
        SQL = '''SELECT messages.person_id, messages.origin_node_id, status, status_location, 
                        status_gps_latitude, status_gps_longitude, status_gps_accuracy, 
                        person_message, imsi, gps_latitude, gps_longitude, gps_accuracy, 
                        timestamp, bio.name_family, bio.name_given, bio.age, bio.sex,
                        sub.submission_id
                 FROM db_person_messages AS messages
     			 JOIN db_submitter_info AS sub 
     			    ON sub.submission_id=messages.submission_id
     			    AND sub.origin_node_id=messages.origin_node_id
     			 LEFT JOIN db_person_bio AS bio 
     			    ON bio.person_id=sub.submitter_id
     			 WHERE messages.person_id = ? 
     			 ORDER BY sub.timestamp DESC'''
     			 
        #execute the query
        results = self._sql(SQL, [person_id]).fetchall()
        
        #put the results in list of dictionaries
        result_dicts = [{name: value for name,value in zip(variables, result)} for result in results]
        
        return result_dicts      
   
        
    def get_next_person_id(self, origin_node_id):
        """
            Return the next person ID to use
        """
        logger.debug("Getting next person ID.")
        
        # Let's not hit the disk if we don't have to
        if self.next_person_id is not None:
            logger.debug("Updating person ID in memory.")
            rtn = self.next_person_id
            self.next_person_id += 1
            return "%d-%d"%(rtn, origin_node_id)
        
        logger.debug("Updating person ID from disk.")
        
        SQL = "SELECT person_id FROM db_person_bio WHERE origin_node_id = ?"
        results = self._sql(SQL, [origin_node_id]).fetchall()
        
        # If it's empty, this is a new database
        if not results:
            self.next_person_id = 2
            return "1-%d"%origin_node_id
        else:
            id_list = [int(r[0].split("-")[0]) for r in results]
            id_list.sort(reverse=True)
            current_id = id_list[0]
            rtn = current_id+1
            self.next_person_id = rtn+1
            return "%d-%d"%(rtn, origin_node_id)
        
        
    def get_next_submission_id(self, origin_node_id):
        """
            Return the next submission ID to use
        """
        logger.debug("Getting next submission ID.")
        
        # Let's not hit the disk if we don't have to
        if self.next_submission_id is not None:
            logger.debug("Updating submission ID in memory.")
            rtn = self.next_submission_id
            self.next_submission_id += 1
            return "%d-%d"%(rtn, origin_node_id)
        
        logger.debug("Updating submission ID from disk.")
        # Query the database to see what the last id was?
        SQL = "SELECT submission_id FROM db_submitter_info WHERE origin_node_id = ?"
        results = self._sql(SQL, [origin_node_id]).fetchall()
        
        # If it's empty, this is a new database
        if not results:
            self.next_submission_id = 2
            return "1-%d"%origin_node_id
        else:
            id_list = [int(r[0].split("-")[0]) for r in results]
            id_list.sort(reverse=True)
            current_id = id_list[0]
            rtn = current_id+1
            self.next_submission_id = rtn+1
            return "%d-%d"%(rtn, origin_node_id)
            
    def get_next_picture_id(self, origin_node_id):
        """
            Return the next picture ID to use
        """
        logger.debug("Getting next picture ID.")
        
        # Let's not hit the disk if we don't have to
        if self.next_picture_id is not None:
            logger.debug("Updating picture ID in memory.")
            rtn = self.next_picture_id
            self.next_picture_id += 1
            return "%d-%d"%(rtn, origin_node_id)
        
        logger.debug("Updating picture ID from disk.")
        # Query the database to see what the last id was?
        SQL = "SELECT picture_id FROM db_pictures WHERE origin_node_id = ?"
        results = self._sql(SQL, [origin_node_id]).fetchall()
        
        # If it's empty, this is a new database
        if not results:
            self.next_picture_id = 2
            return "1-%d"%origin_node_id
        else:
            id_list = [int(r[0].split("-")[0]) for r in results]
            id_list.sort(reverse=True)
            current_id = id_list[0]
            rtn = current_id+1
            self.next_picture_id = rtn+1
            return "%d-%d"%(rtn, origin_node_id)
            
    
    def get_submitter_id(self, db_submitter_info):
        """
            Look up in our tables to see if we can resolv this person
        """
        logger.debug("Looking up submitter person_id.")
        
        # Join identity and submitter to see if we can identify this submitter
        SQL = "SELECT person_id FROM db_submitter_info join db_catan_identity ON db_catan_identity.submission_id=db_submitter_info.submission_id WHERE db_submitter_info.cookie = ? ORDER BY db_catan_identity.timestamp DESC LIMIT 1"
        result = self._sql(SQL, [db_submitter_info.cookie]).fetchone()
        
        # If it's None, this is a new database
        if result is None:
            return -1
        else:
            return result[0]
        
        
    def update_gps(self, node_message):
        """
            Update our database with gps info from our node
        """
        logger.debug("Got a database update message. (GPS)")
        
        # Populate our DB Object
        db_obj = CatanDatabaseObject(node_message.data)
        logger.debug(db_obj)
    
        # Timestamp the message
        if db_obj.timestamp is None:
            db_obj.timestamp = time.time()
        
        # Update the source if we are the first to see the object    
        if node_message.source != 0:
            origin_node_id = node_message.source
        else:
            origin_node_id = self.my_node_id
            
        # Does this packet contain node info
        if db_obj.node_info.has_entries():
            (sql, values) = db_obj.node_info.sql_insert(origin_node_id,
                                              node_message.visited,
                                              timestamp=db_obj.timestamp)
            logger.debug((sql, values))
            self._sql(sql, values)
            
        return db_obj
        
    
    def update_person(self, node_message):
        """
            Update our database with the data parsed from a NodeMessage
        """

        logger.debug("Got a database update message. (Person)")

        # Populate our DB Object
        db_obj = CatanDatabaseObject(node_message.data)
        logger.debug(db_obj)
    
        # Extract info from our CATAN message
        if node_message.source != 0:
            origin_node_id = node_message.source
        else:
            origin_node_id = self.my_node_id
            
        # Timestamp the message
        if db_obj.timestamp is None:
            db_obj.timestamp = time.time()
        
        # Get our submission ID
        if db_obj.submission_id is None:
            db_obj.submission_id = self.get_next_submission_id(self.my_node_id)
        submission_id = db_obj.submission_id
        
        # Try to resolve the submitting person?
        if db_obj.submitter_id is None: 
            db_obj.submitter_id = self.get_submitter_id(db_obj.submitter_info)
        
        origin_person_id = db_obj.submitter_id

        # Is the person specified?
        if db_obj.person_id is None:
            if db_obj.person_bio.name_family is None:
                logger.error("Family name is required for a new person entry.")
                return False
            if db_obj.person_bio.name_given is None:
                logger.error("Given name is required for a new person entry.")
                return False
            if db_obj.person_bio.age is None:
                logger.error("Age is required for a new person entry.")
                return False
            if db_obj.person_bio.sex is None:
                logger.error("Sex is required for a new person entry.")
                return False
            
            db_obj.person_id = self.get_next_person_id(self.my_node_id)
            
            print "** Adding (local) person %s %s to the database (person_id = %s)" % (db_obj.person_bio.name_given, 
                                                                        db_obj.person_bio.name_family,
                                                                        db_obj.person_id)
                                                                        
        else:
            if db_obj.person_bio.name_family and db_obj.person_bio.name_given:
                print "** Adding (remote) person %s %s to the database (person_id = %s)" % (db_obj.person_bio.name_given, 
                                                                        db_obj.person_bio.name_family,
                                                                        db_obj.person_id)
            else:
                print "** Updating person_id = %s" % db_obj.person_id
        
        person_id = db_obj.person_id     
        
        # Check to see if this person is claiming identity
        if db_obj.user_is_submitter:
            identity_sql = db_catan_identity().sql_insert(person_id, 
                                                          submission_id)
            self._sql(identity_sql[0],identity_sql[1])
            origin_person_id = db_obj.submitter_id
        
        # Was a relation to this person claimed?
        if db_obj.person_links.has_entries():
            db_obj.person_links.person_id2 = origin_person_id
        
        # Check each database and update appropriately
        base_dbs = [db_obj.person_bio,
                    db_obj.person_description,
                    db_obj.person_contact,
                    db_obj.person_message,
                    db_obj.person_links
                    ]
        
        # Loop over and update databases appropriately
        for db in base_dbs:
            if db.has_entries():
                sql = db.sql_insert(person_id,
                                      submission_id,
                                      origin_node_id)
                logger.debug(sql)
                self._sql(sql[0],sql[1])
   
        # Special cases below  
            
        # Are they uploading a picture?
        if db_obj.data_picture.has_entries():
            if db_obj.picture_id is None:
                db_obj.picture_id = self.get_next_picture_id(self.my_node_id)
            picture_id = db_obj.picture_id
            picture_data = base64.b64decode(db_obj.data_picture.picture_data)
            # Let's update with our binary version
            
            picture_sql = db_obj.data_picture.sql_insert(picture_id, origin_node_id)
            self._sql(picture_sql[0], picture_sql[1]+[buffer(picture_data)])
            
            picture2_sql = db_obj.person_picture.sql_insert(person_id,
                             submission_id,
                             origin_node_id,
                             picture_id)
            self._sql(picture2_sql[0],picture2_sql[1])

        # Add our submission to the datagbase
        submission_sql = db_obj.submitter_info.sql_insert(submission_id,
                                         origin_node_id,
                                         origin_person_id,
                                         timestamp=db_obj.timestamp)
        self._sql(submission_sql[0],submission_sql[1])

	#log status of the database
	catan.metrics.log_database_counts(self.get_person_counts_by_node())
        
        return db_obj

    
    
class CatanDatabaseObject(object):
    """
        This class defines our object to populate and then convert to a more
        transport-friendly format.
    """

    def __init__(self,data=None):
        """
            If initialized with data, this will parse the JSON and extract
            the attributes back into our class definitions.
            
            @param data: JSON string defining this object
        """
    
        self.person_id = None
        self.user_is_submitter = None
        self.origin_node_id = None
        self.submission_id = None
        self.picture_id = None
        self.timestamp = None
        self.submitter_id = None
         
        self.node_info = db_node_info()
        self.submitter_info = db_submitter_info()
        self.person_bio = db_person_bio()
        self.person_description = db_person_description()
        self.person_contact = db_person_contact()
        self.person_picture = db_person_pictures()
        self.person_links = db_person_links()
        self.person_message = db_person_messages()
        
        self.data_picture = db_pictures()
        
        
        if data is not None:
            self.__unpack__(data)

            
    def __repr__(self):
        """ Returned our packed representation """
        return self.pack()
            
    def __unpack__(self,data):
        """
            Unpack the given data back into our class structures.
        """
        try:
            class_dict = json.loads(data)
        except:
            import traceback
            traceback.print_exc()
            logger.error("Couldn't parse the following data")
            logger.error(data)
            logger.error("Error parsing JSON string in CatanDatabaseObject.")
            return
        
        # Loop over all names and values and set them in this class
        for attr_name, value in class_dict.items():
            self.__set_value__(attr_name, value)
                

    def __set_value__(self, attr_name, value):
        """
            This special function will do the inverse of __get_value__ and
            set the class values given a dict or primative type
        """
        # first ensure the name exist
        if attr_name not in dir(self):
            return False
        
        # Extract attribute
        attr = getattr(self,attr_name)
        
        # Ignore methods
        if inspect.ismethod(attr):
            return False
        
        # Convert classes to dicts
        if isinstance(attr, DBSchema):
            # We can only use dicts
            if isinstance(value, dict):
                attr.__dict__ = dict(attr.__dict__.items() + value.items())
                return True
            else:
                return False
        
        # Otherwise, return the raw value (e.g. str, int)
        self.__setattr__(attr_name, value)
        return True
    
    
    def __get_value__(self, attr_name):
        """
            This is a special function used to convert embedded classes to 
            dictionarys as well as only return attribute values that are 
            relevant to our database
        """
        
        # first ensure the name exist
        if attr_name not in dir(self):
            return None
        
        # Extract attribute
        attr = getattr(self,attr_name)
        
        # Ignore methods
        if inspect.ismethod(attr):
            return None
        
        # Convert classes to dicts
        if isinstance(attr, DBSchema):
            return dict((key, value) for key, value in attr.__dict__.iteritems() 
                            if not callable(value) and not key.startswith('__'))
        
        # Otherwise, return the raw value (e.g. str, int)
        return attr
    
    
    def get_databases(self):
        """
            Simple function to return all of the databases referenced by this
            object
        """
        dbs = []
        for k in dir(self):
            attr = getattr(self,k)
            if isinstance(attr, DBSchema):
                dbs.append(attr)
        return dbs
    
    def pack(self):
        """
            This will pack all of the structure of this class into a JSON object
            for easy transport over networks etc.
        """
        logger.debug("Packing up a database object.")
        
        # Extract our attributes from this class
        attributes = [key for key in dir(self) if not key.startswith('_')]
        
        # Loop over and only populate if they have a non-None value
        rtn_dict = {}
        for a in attributes:
            
            # Extract the value of this particular attribute (value or dict)
            value = self.__get_value__(a)
            
            # Skip any None values
            if value is None:
                continue
            
            # Is this a dict itself?
            if isinstance(value, dict):
                # Filter all None entries so we don't waste network space
                non_none = dict((k,v) for k, v in value.items() if v is not None)
                
                # Only return non-empty dicts
                if len(non_none) > 0:
                    rtn_dict[a] = non_none
            else:
                rtn_dict[a] = value     
        
        json_output = json.dumps(rtn_dict)
        
        return json_output
        
           
class DbHandler(SocketServer.BaseRequestHandler):
    """
         This class is our basic handler for all inputs
    """
    tx_client = TxClient()
    
    def handle(self):
        """
            This function handles any inputs to our tx socket
        """
        sock = self.request
        
        logger.debug("Database handler got message, processing...")
        
        # Receive our header
        node_message = NodeMessage()
        header = sock.recv(len(node_message))
        
        # Receive our data
        node_message._unpack(header)
        if node_message.length > 0:
            node_message.data = sock.recv(node_message.length)
            
        # Grab our mutex to ensure only 1 write at time.
        with db_mutex:
            if node_message.type == G.MESSAGE_TYPE.DB_GPS:
                update_fn = DatabaseServer.DB.update_gps
            elif node_message.type == G.MESSAGE_TYPE.DB_PERSON:
                update_fn = DatabaseServer.DB.update_person
            else:
                logger.error("Got unrecognized DB packet. (Type: %d)"%
                             node_message.type)
                return False
            
            rtn_data = update_fn(node_message)
            if rtn_data is not False:
                logger.debug("Successfully updated db.")
                sock.sendall(`rtn_data`)
            else:
                logger.debug("Db update failed.")
                sock.sendall("0")
                
        
        
class DatabaseServer(TxServer):
    """
        This is our main database server for CATAN.  It will open a unix socket
        at the given location and listen.  It's implement as a socket server
        to mitigate threading concerns, and simplify the api for services.
    """
    
    DB = None
    
    def __init__(self, node_id,
                 socket_name=G.DB_DEFAULT_SOCK,
                 db_filename=G.DB_FILENAME):
        """
            Initialize our socket
            
            @param socket_name: Filename of UNIX socket to open for database 
            interaction.
        """
        
        # Store our socket file name
        self.socket_name = socket_name
        if os.path.exists(self.socket_name):
            try:
                os.unlink(self.socket_name)
            except:
                logger.error("Could not delete %s, socket creation will fail."%
                             self.socket_name)
                
        
        DatabaseServer.DB = CatanDatabase(node_id=node_id,
                                          filename=db_filename)
        
        # Setup our server
        self.server = SocketServer.UnixStreamServer(socket_name,DbHandler)
        
        # IMPORTANT: Allow everyone to write to the socket
        os.chmod(socket_name, 0777)
        
        multiprocessing.Process.__init__(self)
        
        


class DatabaseClient(TxClient):
    """
        This class is the API to properly interact with our Database server
    """
    
    def __init__(self,server_name=G.DB_DEFAULT_SOCK):
        """
            Initialize with the filename of our UNIX socket
            
            @param server_name: Name of our database socket name
        """

        self.server_name = server_name
    
    
    def _send(self, node_message):
        """
            Send a packed database message to our database server and get the 
            response.
            
            @param node_message: CATAN NodeMessage with raw database message as
            the data
        """
        try:
            # Create a socket (SOCK_STREAM means a TCP socket)
            self.SOCK = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
            # Connect to server and send data
            self.SOCK.connect(self.server_name)
        
            # Send the message
            rtn = self.SOCK.sendall(`node_message`)
            
            if rtn is None:
                rtn2 = self.SOCK.recv(1024)
                return rtn2
            else:
                return False
            
        except:
            logger.error("Failed to send message to our DB server.")
            import traceback
            traceback.print_exc()
        
        finally:
            self.SOCK.close()
            
        return False
             
