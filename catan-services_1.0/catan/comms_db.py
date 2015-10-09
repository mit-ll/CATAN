"""
    This database will be used to keep track of all our messages for retransmission purposes.

    (c) 2015 Massachusetts Institute of Technology
"""

# Native
import multiprocessing
import time
import os
import struct
import json
import logging
logger = logging.getLogger(__name__)

# 3rd Party
import sqlite3

# CATAN
import catan.globals as G
from catan.data import NodeMessage, RetransmitReq
from catan.globals import MESSAGE_TYPE

MUTEX = multiprocessing.Lock()




class RetransmissionDatabase:
    
    def __init__(self, filename=G.DB_MSG_FILENAME):
        """
            Initialize and connect to our databse.
        """
        self.filename = filename
        self.CONN = None
        
        self._connect()
        
    
    def __create(self):
        """
            Create our database schema
        """
        
        try:
            with MUTEX:
                c = self.CONN.cursor()
                
                # Create a database for sent messages
                c.execute('''CREATE TABLE messages_sent
                (message_id int, source_node_id int, message_type int, data blob, timestamp real)''')
                
                # Create a database for received messages
                c.execute('''CREATE TABLE messages_received
                (message_id int, source_node_id int, message_type int, timestamp real)''')
                
                # Create a database for received messages
                c.execute('''CREATE TABLE messages_retransmissions
                (message_id int, source_node_id int, message_type int, timestamp real)''')
                
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
            self.CONN.text_factory = str
        except:
            logger.error("Could not connect to database. (%s)"%self.filename)
            self.CONN = None
            return False
            
        # Create all of our tables
        if init:
            return self.__create()
        else:
            return True
        
        
    def _sql(self, cmd, fields=[]):
        """
            Perform our SQL command
            
            @param sql: SQL string
            @param fields: list of fields to substitue into SQL sring
        """
        rtn = None
        
        with MUTEX:
            try:
                c = self.CONN.cursor()        
                
                rtn = c.execute(cmd, fields)
        
                self.CONN.commit()
            except:
                logger.error("Could not query database.")
                logger.error("Query: %s %s"%(cmd,fields))
                
                import traceback
                traceback.print_exc()
                return None
                
        return rtn
    
    
    def clean_old_records(self):
        """
            Clean all records that are older than a predefined time.
        """
        
        # Calculate our cutoff
        cuttuf_timestamp = time.time()-G.RETRANSMISSION_MAX_RECORD_AGE
        
        # Delete old records
        self._sql("DELETE FROM messages_sent WHERE timestamp < ?", 
                  [cuttuf_timestamp])
        self._sql("DELETE FROM messages_received WHERE timestamp < ?",
                  [cuttuf_timestamp])
        
        
    def get_last_message_id_recv(self, message_type, source_node_id):
        """
            Return the last messge id of this type from this particular node.
            
            @param message_type: Type of message
            @param source_node_id: Source of message 
        """
        
        SQL = """
            SELECT message_id FROM messages_received 
            WHERE message_type=? AND source_node_id=?
            ORDER BY message_id
            LIMIT 1
            """
        result = self._sql(SQL, [message_type, source_node_id]).fetchone()
        
        if result is None:
            return None
        else:
            return result[0]
        
        
    def is_retransmission(self, message_type, source_node_id, message_id):
        """
            Return the last messge id of this type from this particular node.
            
            @param message_type: Type of message
            @param source_node_id: Source of message 
        """
        
        SQL = """
            SELECT message_id FROM messages_sent
            WHERE message_type=? AND source_node_id=? AND message_id=?
            ORDER BY message_id
            LIMIT 1
            """
        params = [message_type, source_node_id, message_id]
        result = self._sql(SQL, params).fetchone()
        
        if result is None:
            return False
        else:
            return True
    
    
    def store_received_message(self,node_message):
        """
            Store the relevant information for a received message.
        
            @param node_message: CATAN Node message that was received over the 
                                    network.
        """
        # Only process select messages
        if node_message.type == G.MESSAGE_TYPE.RT_NODE_ANNOUNCEMENT:
            logger.debug("Node announcement: checking to see if we missed packets.")
            # Extract our dict
            node_msg_dict = json.loads(node_message.data)
            for message_type in node_msg_dict:
                message_id = int(node_msg_dict[message_type])
                # Store
                self._check_dropped_messages(node_message.source, 
                                     int(message_type), 
                                     message_id)
                
        if node_message.type not in G.RETRAMISSION_MESSAGE_TYPES:
            return False
        
        self._check_dropped_messages(node_message.source, 
                                     node_message.type, 
                                     node_message.id)
        
        
    def _check_dropped_messages(self, source_id, message_type, message_id,
                                store_new=True):
        
        
        # Define our SQL statements
        SQL_INSERT = """
                INSERT INTO messages_received
                ('message_id', 'source_node_id', 'message_type', 'timestamp')
                VALUES (?,?,?,?)
                """
        SQL_INSERT_RETRANS = """
                INSERT INTO messages_retransmissions
                ('message_id', 'source_node_id', 'message_type', 'timestamp')
                VALUES (?,?,?,?)
                """
        SQL_UPDATE = """
                UPDATE messages_received
                SET message_id = ?,
                timestamp = ?
                WHERE source_node_id = ?
                AND message_type = ?
                """
                
        logger.debug("Logging message (id: %d, type: %d) from %d"%(message_id,
                                                                   message_type,
                                                                   source_id))
        if store_new:
            logger.debug("Storing as a new message.")
        
        # Are we missing packets?
        last_id = self.get_last_message_id_recv(message_type,
                                               source_id)
        
        # Looks like this is the first entry
        if last_id is None:
            logger.debug("First messgae of this type.")
            if store_new:
                result = self._sql(SQL_INSERT, [message_id,
                                     source_id,
                                     message_type,
                                     time.time()])
            # Assume that all ids started at 1, so be sure to include it.
            last_id = 0
            
            
        # Normal message in sequence
        if message_id > last_id:
            logger.debug("In sequence messgae of this type.")
            # Add any dropped packets to our retransmission database.
            for dropped_id in range(last_id+1,message_id):
                logger.debug("Missing message id %d from %d"%(dropped_id,
                                                            source_id))
                result = self._sql(SQL_INSERT_RETRANS, [dropped_id,
                                     source_id,
                                     message_type,
                                     time.time()])
            
            # Update our current record.
            if store_new:
                result = self._sql(SQL_UPDATE, [message_id,
                                     time.time(),
                                     source_id,
                                     message_type])
            
        # Retransmitted message
        else:
            logger.debug("Re-transmitted messgae of this type.")
            # Remove packet from retransmit
            SQL_DEL = """
                        DELETE from messages_retransmissions
                        WHERE source_node_id = ? 
                        AND message_type = ?
                        AND message_id = ?
                    """
            if store_new:
                result = self._sql(SQL_DEL, [source_id,
                                 message_type,
                                 message_id])

        if result is None:
            return False
        else:
            return True
    
    
    def store_sent_message(self,node_message):
        """
            Store a sent message in case we need to replay it.
            
            @param node_message: CATAN Node message that was sent over the 
                                    network.
        """
        
        # Is this a type that we re-transmit?
        if node_message.type not in G.RETRAMISSION_MESSAGE_TYPES:
            return False
        
        # Don't store re-transmissions
        if self.is_retransmission(node_message.type, 
                                  node_message.source,
                                  node_message.id):
            logger.debug("Looks like we have a re-transmission, skipping db.")
            return False
        
        SQL = """
            INSERT INTO messages_sent
            ('message_id', 'source_node_id', 'message_type', 'data', 'timestamp')
            VALUES (?,?,?,?,?)
            """
        
        result = self._sql(SQL, [node_message.id,
                                 node_message.source,
                                 node_message.type,
                                 `node_message`,
                                 time.time()])
        
        logger.debug("Stored a copy of the message in the database")
        
        if result is None:
            return False
        else:
            return True
        
        
    def get_sent_message(self,message_id,source_node_id,message_type):
        """
            Retrieve the sent message from our database.
            
            @param message_id: Message ID
            @param source_node_id: Source ID of original message
            @param message_type: Message type
        """
        
        SQL = """
            SELECT data FROM messages_sent
            WHERE message_id=?
            AND source_node_id=?
            AND message_type=?
            ORDER BY timestamp
            """
        
        result = self._sql(SQL, [message_id,
                                 source_node_id,
                                 message_type]).fetchone()
        if result is None:
            return result
        else:
            return NodeMessage(result[0])
        
    def get_retransmissions(self):
        """
            Return a list of retransmission data requests
        """
        
        SQL = """
                SELECT source_node_id, message_type, message_id
                FROM messages_retransmissions
                ORDER BY timestamp DESC
            """
            
        result = self._sql(SQL)
        
        if result is None:
            return []
        
        # package in a binary format and return the list
        rtn = {}
        
        # Let's first group them
        rtn_dict = {}
        for row in result:
            # 0 - Source
            if row[0] not in rtn_dict:
                rtn_dict[row[0]] = {}
            # 1 - Type
            if row[1] not in rtn_dict[row[0]]:
                rtn_dict[row[0]][row[1]] = []
            # 2 - ID
            rtn_dict[row[0]][row[1]].append(row[2])
            
        # Now only create one packet for each source/type pair
        for source in rtn_dict:
            for type in rtn_dict[source]:
                ids = rtn_dict[source][type]
                req = RetransmitReq()    
                req.source = source
                req.type = type
                req.count = len(rtn_dict[source][type])
                req.data = struct.pack("%dI"%req.count, *ids)
                    
                rtn[source] = req
            
        return rtn
        
        
    def get_message_id_dict(self, node_id):
        """
            Return a dict for our current message id counters
        """
        SQL = """
                SELECT DISTINCT message_type, MAX(message_id)
                FROM messages_sent
                WHERE source_node_id = ?
                GROUP BY message_type
            """
            
        result = self._sql(SQL, [node_id])
        
        # package in a binary format and return the list
        rtn = {}
        for row in result:
            rtn[row[0]] = int(row[1])+1
            
        return rtn