# © 2015 Massachusetts Institute of Technology
import sys
import logging
logger = logging.getLogger(__name__)
import multiprocessing
import serial

import catan.ax25 as ax25


class AX25_KISS_RxServer(multiprocessing.Process):
    
    def __init__(self, node_id, port='/dev/ttyUSB0'):
        """ 
            Intitilize our Receiver.
        
            @param node_id: provide the local node ID so we can filter 
                    appropriately
            @param port: provide the serial device that the server
                    will read from
        """
        self.my_node_id = node_id
        try:
            ser = serial.Serial(port, 9600)
            ser.timeout = .01
            logger.debug("Using "+port)
            self.ser = ser
        except OSError as err:
            logger.error( err )
            logger.error("Couldn't open serial connection")
            self.ser = None
        
        multiprocessing.Process.__init__(self)
        
    def get_message(self):
        """
            Get a message from our backlink
        """
        return RX_QUEUE.get()
        
    def serve_forever(self):
        """
            This method will loop forever and appropriately handle all of our 
            received messages, either processing them or forwarding them.
        """

        buf = ''
        # Main program loop    
        while True:
            # Read serial line
            if self.ser <> None:
                s = self.ser.read(1000)
                try:
                    n = len(s)
                except TypeError:
                    n = 0       
            else:
                n = 0                
            
            # Process received data          
            if n <> 0:
                lst = []
                
                w = s.split(chr(0xc0))
                n = len(w)
                
                # No 0xc0 in frame
                if n == 1:
                    buf += w[0]
            
                # Single 0xc0 in frame
                elif n == 2:
                    # Closing 0xc0 found
                    if w[0] <> '':
                        # Partial frame continued, otherwise drop
                        lst.append(buf + w[0])
                        buf = ''
            
                    # Opening 0xc0 found
                    else:
                        lst.append(buf)
                        buf = w[1]
            
                # At least one complete frane received
                elif n >= 3:                   
                    for i in range(0, n - 1):
                        st = buf + w[i]       
                        if st <> '':
                            lst.append(st)
                            buf = ''         
                    if w[n - 1] <> '':
                        buf = w[n - 1]                

                # Loop through received frames
                for p in lst:
                    if len(p) == 0:
                        continue                       
                    if ord(p[0]) == 0:
                        hex_str = " ".join([ "{:02x}".format(ord(c)) for c in p[1:] ])
                        #logger.debug("MSG RAW (HEX): "+hex_str)
                        raw_str = ax25.kiss2raw(p[1:])
                        msg_tuple = ax25.parse_raw_msg(raw_str)
                        if msg_tuple:               
                            strfrom, strto, msg_data, digis = msg_tuple         
                            #logger.debug(msg_data)
                            #if len(msg_data) < MESSAGE_HEADER_LEN:
                            #    logger.error("Did not receive enough \
                            #                  data to be a NodeMessage.")
                            #    #logger.error(`msg_data`)
                            #    continue
                            
                    	    #Convert to Node Message
                            #node_msg = NodeMessage(msg_data)
                            print msg_data

                            #if node_msg is not None:    
                                #Add to queue  
                                # Filter messages from our self.  (Pretty likely with RF)
                                #if node_msg.source == self.my_node_id:
                                #    logger.debug("Got message from myself, ignoring.")
                                #    continue
                                # Add to our RX queue
                                #RX_QUEUE.put((node_msg, strfrom))
                    # Control frame received
                    else:
                        pass
            
    def run(self):
        self.serve_forever()
        

def main():
    if len(sys.argv) > 1:
        myport = sys.argv[1]
    else: 
        print "Usage: %s PORT" % sys.argv[0]
        exit(1)
        
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        receiver = AX25_KISS_RxServer(1, myport)
    except serial.SerialException as e:
        print e
        exit(1)
        
    receiver.run()
    
    print "Rx done"
    
if __name__ == "__main__":
    main()
    
