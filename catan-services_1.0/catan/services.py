"""
    This will define numerous background services that will be running on our 
    CATAN nodes
    
    (c) 2015 Massachusetts Institute of Technology
"""
# Native
import multiprocessing
import logging
logger = logging.getLogger(__name__)
import time
import json

# CATAN
import catan.globals as G
import catan.utils as utils
from catan.comms import TxClient, TxScheduler
from catan.db.node import CatanDatabaseNodeObject

class NodeAnnouncementService(multiprocessing.Process):
    """
        This service will run in the background and periodically announce
        this node's presence over the data link
    """

    def __init__(self, tx_socket, 
                 is_gateway=False,
                 db_client=None,
                 db_retrans=None, 
                 gps_receiver=None,
                 node_id=None):
        """
            Store our gateway status and tx_socket filename
        """
        self.is_gateway = is_gateway
        self.tx_socket = tx_socket
        
        self.db_client = db_client
        self.gps_receiver = gps_receiver
        
        self.db_retrans = db_retrans
        self.node_id = node_id
        
        multiprocessing.Process.__init__(self)

    def run(self):
        """
            Peridocially send an announcement packet over our datalink
        """
        tx_client = TxClient(self.tx_socket)
        gps_prev = None
        while True:
            logger.debug("Announcing Presence.")
            
            if self.db_retrans is not None:
                # Get a dict of all our current message ids
                msg_dict = self.db_retrans.get_message_id_dict(self.node_id)
                tx_client.send(G.MESSAGE_TYPE.RT_NODE_ANNOUNCEMENT,
                           json.dumps(msg_dict) )
            else:
                tx_client.send(G.MESSAGE_TYPE.RT_NODE_ANNOUNCEMENT)
                
            # Checking for GPS
            if self.gps_receiver is not None and self.db_client is not None:
                
                # Get our GPS coords
                logger.debug("Getting GPS coordinates")
                gps_info = self.gps_receiver.get_coordinates()

                # If we got GPS data, report it.
                if gps_info is None:
                    logger.error("Could not receive GPS info.")
                    
                elif gps_info != gps_prev:
                    logger.debug("Sending GPS info: %s"% gps_info)
                    db_obj = CatanDatabaseNodeObject()
                    db_obj.node_info.gps_latitude = gps_info['latitude']
                    db_obj.node_info.gps_longitude = gps_info['longitude']
                    db_obj.node_info.gps_altitude = gps_info['altitude']
                    db_obj.node_info.gps_sat_count = gps_info['satillite_count']
                    
                    logger.debug("Sending GPS info to databse.")
                    self.db_client.send(G.MESSAGE_TYPE.DB_GPS,`db_obj`)
                    logger.debug("Sending GPS info to other nodes.")
                    tx_client.send(G.MESSAGE_TYPE.DB_GPS,`db_obj`)
                    
                # Update previous               
                gps_prev = gps_info
                
                # Update our time using our GPS
                logger.debug("Getting time/date date from GPS.")
                gps_time = self.gps_receiver.get_time()
        
                if gps_time is not None:
                    logger.debug("Updated time to: %s"%gps_time)
                    utils.linux_set_time(gps_time.timetuple())

            # No reason to beat this to death
            time.sleep(G.RT_NODE_ANNOUNCEMENT_DELAY)
            
