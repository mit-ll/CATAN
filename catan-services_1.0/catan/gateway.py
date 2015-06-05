"""
    This file contains all the CATAN gateway operations 
      for uploading data to Google Person Finder
    
    @author: Ben Bullough
    @organization: MIT Lincoln Laboratory
    © 2015 Massachusetts Institute of Technology
"""

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import time
import urllib2
import logging
LOGGER = logging.getLogger(__name__)

# CATAN
from db import CatanDatabase
import catan.globals as G


def make_xml(root):
    """
        Converts an element hierarchy to an xml document and 
        returns it as a string
    """

    raw_string =  ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(raw_string)
    pretty_string = reparsed.toprettyxml(indent="  ")
    
    return pretty_string


class PersonFinderUploader:
    """
        This class implements the interface to Google Person Finder
    """
    def __init__(self, source, record_prefix, url, delay):
        self.source = source
        self.record_prefix = record_prefix
        self.url = url
        self.delay = delay

                
    def make_person_element(self, person_dict):
        """
            Create a PFIF Person element object from a dictionary
        """     
        person = ET.Element("pfif:person")
        
        #person_record_id
        field = ET.SubElement(person, "pfif:person_record_id")
        field.text = self.record_prefix+str(person_dict['person_id'])
        
        #source_date
        time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", 
                                 time.gmtime(person_dict['timestamp']))
        field = ET.SubElement(person, "pfif:source_date")
        field.text = str(time_str)

        #full_name
        field = ET.SubElement(person, "pfif:full_name")
        field.text = " ".join([person_dict['name_given'], 
                               person_dict['name_family']])
        
        #source_name
        field = ET.SubElement(person, "pfif:source_name")
        field.text = self.source

        #other fields
        mapping = {'name_given': 'pfif:given_name',
                   'name_family': 'pfif:family_name',
                   'person_description': 'pfif:description',
                   'sex': 'pfif:sex',
                   'age': 'pfif:age',
                   'street': 'pfif:home_street',
                   'neighborhood': 'pfif:home_neighborhood',
                   'city': 'pfif:home_city',
                   'state': 'pfif:home_state',
                   'zip': 'pfif:home_postal_code',
                   'country': 'pfif:home_country',
                   }
                                           
        for key, value in mapping.items():
            if key in person_dict and person_dict[key]:
                field = ET.SubElement(person, value)
                field.text = person_dict[key]    
                
        return person        
       
    def make_note_element(self, note_dict):
        """
            Create a PFIF Note element object from a dictionary
        """               
        note = ET.Element("pfif:note")
        
        #note_record_id
        field = ET.SubElement(note, "pfif:note_record_id")
        field.text = self.record_prefix+str(note_dict['person_id'])+"." \
                                  +str(note_dict['origin_node_id'])+"." \
                                  +str(note_dict['submission_id'])
                                  
        #person_record_id
        field = ET.SubElement(note, "pfif:person_record_id")
        field.text = self.record_prefix+note_dict['person_id']
             
        #source_date
        time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", 
                                 time.gmtime(note_dict['timestamp']))
        field = ET.SubElement(note, "pfif:source_date")
        field.text = str(time_str)
                
        #author_name
        field = ET.SubElement(note, "pfif:author_name")
        if note_dict['sub_name_given'] and note_dict['sub_name_family']:
            field.text = " ".join([note_dict['sub_name_given'], 
                                   note_dict['sub_name_family']])
        else:
            field.text = "Unknown"
        
        #text
        field = ET.SubElement(note, "pfif:text")
        field.text = note_dict['person_message']        
        
        #Optional
        #author_email       
        #author_phone
        #status  (need correct options)
        #email_of_found_person
        #last_known_location
        #email_of_found_person
        #phone_of_found_person
        #other fields
        mapping = {}
                                           
        for key, value in mapping.items():
            if key in note_dict and note_dict[key]:
                field = ET.SubElement(note, value)
                field.text = note_dict[key]                          
                
        return note
               
    def generate_tree(self, since=0):
        """
            Creates a hierarchy of elements representing the data to upload
        """    
        root = ET.Element("pfif:pfif", 
                          {'xmlns:pfif':'http://zesty.ca/pfif/1.4'})
        
        cdb = CatanDatabase(node_id=1, filename=G.DB_FILENAME)
        if not cdb or cdb.CONN is None:
            LOGGER.error("Could not connect to database")
            return None
        
        person_ids = cdb.get_person_ids()

        for person_id in person_ids:
            person_dict = cdb.get_person_info(person_id)
            if person_dict['timestamp'] > since:
                person_elem = self.make_person_element(person_dict)
                root.append(person_elem)
 
        for person_id in person_ids:
            messages_list = cdb.get_messages_by_person(person_id)
            for msg_dict in messages_list:
                if msg_dict['timestamp'] > since:
                    note_elem = self.make_note_element(msg_dict)
                    root.append(note_elem)       

        return root

    def print_list(self, since=0):
        """
            Prints the full name for each Person record to upload to stdout
        """
        tree = self.generate_tree(since)
                
        if tree is not None:
            for root in tree.iter("pfif:pfif"):
                for person in root.iter("pfif:person"):
                    for item in person.iter("pfif:full_name"):
                        print item.text                
    
    def send(self, xml_str):
        """
            Connects to the Person Finder instance and uploads
            data via an HTTP POST request
        """
        request = urllib2.Request(self.url)
        request.add_header('Content-type', 'application/xml')
        request.add_data(xml_str)

        #print "Waiting for response..."
        try:
            response = urllib2.urlopen(request)
            LOGGER.debug(response.read())
            return True
        except urllib2.HTTPError as err:
            LOGGER.error(err)
            LOGGER.error(err.geturl())
            LOGGER.error(err.info())
            return False
        except urllib2.URLError as err:
            LOGGER.error(err)
            return False
                       
    def upload(self, since=0):
        """
            Retrieves updated data and sends it to the Person Finder instance
        """
        tree = self.generate_tree(since)
        if tree is not None:
            xml_str = make_xml(tree)
            return self.send(xml_str)
        else:
            return False
                    
    def run(self):
        """
            Monitors the database for new/updated records and
            uploads them to Person Finder
        """
        LOGGER.info("Starting gateway with updates every %d seconds" % 
                    self.delay)
        last_update = 0
        while True:
            LOGGER.info("Sending updates since %f" % last_update)
            attempt_time = time.time()
            
            if self.upload(since=last_update):
                LOGGER.info("  Successful update")
                last_update = attempt_time
            else:
                LOGGER.info("  Update failed")
            time.sleep(self.delay)

    

