"""
    This our simple database server and should be the only interface for 
    database updates to ensure thread saftey.
    
    Note: This is for debug purposes only.
    
    @author: Chad Spensky
    © 2015 Massachusetts Institute of Technology
"""

# Native
import sys
import logging
logger = logging.getLogger(__name__)

# CATAN
from catan.db import DatabaseServer
import catan.globals as G

def catan_database(args):
    """
        Open our database server socket and listen forever.
    """
    db_server = DatabaseServer(args.node_id,
                               db_filename=args.sqlite_database)
    
    db_server.serve_forever()



if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--node_id", type=int, default=None,
                        help="Assign this node a particular Node ID.")
    parser.add_argument("-s", "--sqlite_database", type=str, 
                        default=G.DB_FILENAME, help="Name of sqlite database.")
    parser.add_argument("-d", "--debug", action="store_true", default=False,
                        help="Enable debugging output.")
    args = parser.parse_args()
    
    if args.debug:
        print "* DEBUG Enabled."
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()
    
    if args.node_id is None:
        logger.error("You must provide a Node ID.")
        parser.print_help()
        sys.exit(0)
        
    if args.node_id < 1 or args.node_id > 255:
        logger.error("Node IDs must be between 1 and 255.  (0 is the broadcast address.)")
        parser.print_help()
        sys.exit(0)
        
    catan_database(args)
