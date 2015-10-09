"""
    All of the classes which handle our RX communication for our CATAN nodes.
    
    (c) 2015 Massachusetts Institute of Technology
"""

import multiprocessing

class RxServer(multiprocessing.Process):
    
    def __init__(self,rx_backlink,tx_backlink=None):
        """
            Intitilize our Receiver with the appropriate backlinks.  Both RX 
            and TX are required for forwarding.
        
            @param rx_backlink:  Backlink receiver object
            @param tx_backlink: Backlink transmit object 
        """
        
        self.rx_backlink = rx_backlink
        self.tx_backlink = tx_backlink
        
        multiprocessing.Process.__init__(self)
        
        
    def get_message(self):
        """
            Get a message from our backlink
        """
        
        return self.rx_backlink.recv()
        
    def serve_forever(self):
        """
            This method will loop forever and appropriately handle all of our 
            received messages, either processing them or forwarding them.
        """
        
        
        while True:
        
            print "Receiving data..."
            msg = self.rx_backlink.recv()
            
            print "RxServer:"
            print msg
            
    def run(self):
        self.serve_forever()