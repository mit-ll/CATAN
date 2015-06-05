#!/usr/bin/env python
"""
    This is our TX server that will listen on the appropriate UNIX socket and
    server as general API to all of our services.
    
    @author: Chad Spensky
    © 2015 Massachusetts Institute of Technology
"""
# Native
import time
import logging
logger = logging.getLogger(__name__)

# CATAN
from catan.comms import TxServer
from catan.datalink import UDPTransmitter
import catan.globals as G


if __name__ == "__main__":
    
    logging.basicConfig()
    
    node_id = 0
    node_dict = { #NodeID   :         (IP, PORT) 
                    0       : ('127.0.0.1',G.UDP_DEFAULT_PORT)
                 }
    
    # Initialize our low-level transmitter
    udp_transmit = UDPTransmitter(node_id,node_dict)
    
    # Start our server
    server = TxServer(udp_transmit,G.TX_DEFAULT_SOCK)
    
    server.serve_forever()
    
