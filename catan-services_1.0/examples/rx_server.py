#!/usr/bin/env python
"""
    This starts up the appropriate backlink and start are RX server to start
    consumming CATAN messages. 
    
    (c) 2015 Massachusetts Institute of Technology
"""
#Native
import logging
logger = logging.getLogger(__name__)

# CATAN
from catan.datalink import UDPReceiver
from catan.rx import RxServer


if __name__ == "__main__":
    
    logging.basicConfig()
    
    # Setup backlink
    node_id = 0
    
    receiver = UDPReceiver(node_id)
    
    # start our server
    rx_server = RxServer(receiver)

    rx_server.serve_forever()
    
    