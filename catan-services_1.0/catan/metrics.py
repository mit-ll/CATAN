"""
    This file contains code to measure the performance of the system 
    
    @author: Ben Bullough    
    © 2015 Massachusetts Institute of Technology
"""

# Native
import logging
LOGGER = logging.getLogger(__name__)
import time
import re

# CATAN
import catan.db
import catan.globals as G

def log_database_counts(node_dict):
    """
        This function writes the number of persons in the database that
        originated from each node to a log file 
        
        Primarily used for testing synchronization of the node databases
    """

    with open(G.METRICS_DBSYNC_LOG_FILENAME, 'a') as log:
        log.write("Time = %d, Nodes = %s\n" % ( int(round(time.time())), 
                                               str(node_dict) ) )


def log_person_update(node_message):
    """
        This function takes a node message containing a person update and
        logs the communication delay based on the time encoded in the message

	called from catan_services
    """

    db_obj = catan.db.CatanDatabaseObject(node_message.data)
    diff_time = None
    if db_obj.person_description:        
        if db_obj.person_description.person_description:
            description = db_obj.person_description.person_description   
            diff_time = extract_time_diff(description)
            msg_type = "Person"     
    elif db_obj.person_message:
        if db_obj.person_message.person_message:
            message = db_obj.person_message.person_message
            diff_time = extract_time_diff(message)
            msg_type = "Message"
            
    if diff_time:
        with open(G.METRICS_UPDATE_LOG_FILENAME, 'a') as log:
            log.write("Time = %d, Delay = %d, Node = %d, Type = %s\n" 
                     % (int(round(time.time())), diff_time, 
                        node_message.source, msg_type ) )
            

def extract_time_diff(text):
    """
        Returns the difference between the current time and the time
        in the embedded << >> tag (encoded in POSIX time)
        or None if a matching tag cannot be found
    """

    time_list = re.findall('<<(.*)>>', text)
    if time_list:
        update_time = float(time_list[0])
        diff_time = round(time.time() - update_time)
        return diff_time
    else:
        return None
        
    
    
