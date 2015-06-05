#!/usr/bin/env python
"""
    This is just a simple test client
    © 2015 Massachusetts Institute of Technology
"""

# Native
import socket
import sys
import random
import logging
logger = logging.getLogger(__name__)

# CATAN
import catan.globals as G
from catan.data import NodeMessage
from catan.comms import TxClient

data = "Test"

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--remote_node_id", type=int, default=0,
                        help="Send test message to remote node id.")
    parser.add_argument("-d", "--debug", action="store_true", default=False,
                        help="Enable debugging output.")
    parser.add_argument("-m", "--message", type=str, default="Test",
                        help="Message to send as data")
    args = parser.parse_args()
    
    if args.debug:
        print "* DEBUG Enabled."
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()
    
    data = args.message
    
    # Create a TxClient
    client = TxClient(G.TX_DEFAULT_SOCK)
    
    rtn = client.send(0,
            data,
            destination=args.remote_node_id)
    
    if rtn:
        print "Sent: ",
        print data
    else:
        print "Error Sending message"
