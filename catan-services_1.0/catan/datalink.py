"""
    This file contains all of the actuall low-level datalink interfaces for 
    CATAN
    
    @author: Chad Spensky
    @organization: MIT Lincoln Laboratory
    © 2015 Massachusetts Institute of Technology
"""

# Native
import socket
import logging
import time
import IN
logger = logging.getLogger(__name__)

# CATAN
import catan.globals as G
from catan.data import NodeMessage


# AX25
from data import UDPHeader
import catan.ax25 as ax25
import serial

# Constansts
MESSAGE_HEADER_LEN = len(NodeMessage()) 


class LinkTransmitter:

        
        
    def send(self,node_message):
        """
           Send a NodeMessage to the proper node referenced by its node id.
           
            @param node_message: an object that is of type NodeMessage
        """
        logger.debug("LinkTransmitter sending message of length %d" % len(node_message))
            
        self._send(node_message)
        
        
    def _send(self, node_message):
        """
            Send data over the desired data link
        """
        raise("Unimplemented Function")
        
        
class LinkReceiver:
        
    
    def recv(self):
        """
            Receive the next NodeMessage from our data link
        """
        logger.debug("LinkReceiver receiving message.")
        
        # Keep trying until we get something
        while True:
            recv_data = self._recv()
            if recv_data is not None:
                return recv_data
    
    def _recv(self):
        """
            Receive a node message over desired data link
        """
        raise("Unimplemented Function")
    
        
class UDPTransmitter(LinkTransmitter):
    """
        Define our low-level link protocol functions
    """
    def __init__(self,
                 port=G.UDP_DEFAULT_PORT, 
                 broadcast_address=G.UDP_BROADCAST_ADDRESS,
                 iface=G.UDP_DEFAULT_INTERFACE):
        """
            Store our  port for UDP
        """
        self.port = port
        self.broadcast_address = broadcast_address
        self.iface = iface
    
    def _send(self, node_message):
        """
            Send a broadcast message on UDP
            
            @param node_message: NodeMessage object to send over the network
        """
        # Open socket, send data
        try:
#             sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            sock = socket.socket(socket.AF_INET, 
                                               socket.SOCK_RAW, 
                                                socket.IPPROTO_UDP) # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Bind to our mesh interface
            try:
                sock.setsockopt(socket.SOL_SOCKET,
                                        IN.SO_BINDTODEVICE,
                                        self.iface+'\0')
            except:
                logger.warn("Your kernel doesn't support binding to an " \
                            "interface.  Your packets may be going out on the" \
                            " wrong interface")

            udp_packet = UDPHeader(`node_message`)
            udp_packet.port_dst = self.port
            udp_packet.length = len(udp_packet)
            
            sock.sendto(`udp_packet`, (self.broadcast_address, self.port))
            
            logger.debug("Sent message to '%s'."%self.broadcast_address)
                
            sock.close()
        except:
            import traceback
            traceback.print_exc()
            logger.error("Could not send message over UDP")
            
        
        # Emulate a slower link
        if G.UDP_TX_LIMIT > 0:
            seconds = (len(node_message)*1.0)/(G.UDP_TX_LIMIT*.10)
            logger.debug("Emlulating a slow link, sleeping %d seconds..."%
                         seconds)
            time.sleep(seconds)
    
    
class UDPReceiver(LinkReceiver):
    
    def __init__(self,port=G.UDP_DEFAULT_PORT,iface=G.UDP_DEFAULT_INTERFACE):
        """
            Initialize UDP listener
        """
        self.port = port
        self.iface = iface
        
        self.SOCK = None
        self._connect()
        
        
    def _connect(self):
        """
            Bind our UDP server
        """
        try:
            #self.SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            self.SOCK = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP) # UDP
#             self.SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, self.iface)
            self.SOCK.bind( ("0.0.0.0",self.port) )
        except:
            logger.error("Couldn't listen on port %d"%self.port)
            self.SOCK = None
    
    
    def _recv(self):
        """
            Receive a node message over UDP
        """
        if self.SOCK is None:
            try:
                self._connect()
            except:
                logger.error("No socket exist.  Aborting receive.")
                return None
                
        (msg_data, addr) = self.SOCK.recvfrom(G.UDP_MAX_SIZE)
        
        # Strip off IP header
        ip_header_len = (ord(msg_data[0]) & 0xf) * 4
        msg_data = msg_data[ip_header_len:]

        udp_header = UDPHeader(msg_data[:8])
        
        if udp_header.port_dst != self.port:
            return None
        
        # Strip off UDP header
        msg_data = msg_data[8:]

        if len(msg_data) < MESSAGE_HEADER_LEN:
            logger.error("Did not receive enough data to be a NodeMessage.")
            logger.error(`msg_data`)
            return None
        
        # Extract our header
        node_message = NodeMessage(msg_data)
 
        #return a list of (message, addr) tuples        
        return [(node_message, addr)]


class AX25_KISS_Transmitter(LinkTransmitter):
    """
        Define our KISS mode AX25 link protocol transmit functions   
    """
    
    def __init__(self, callfrom, port='/dev/ttyUSB0'):
        """
            Store our port for AX25
            
            @param callfrom: the sending callsign
            @param port: the serial port for the KISS mode device
        """
        self.port = port
        self.call = callfrom
        self.next_send_time = time.time()
        try:
            ser = serial.Serial(port, 9600)
            ser.timeout = 1
            
            logger.debug("Transmitter using "+port)
            self.ser = ser
        except OSError as err:
            logger.error( err )
            logger.error("Couldn't open serial connection")
            self.ser = None
    
    def send(self, node_message):
        """
           Send a NodeMessage to the proper node referenced by its node id.
           
            @param node_message: an object that is of type NodeMessage
        """
        #logger.debug("AX25_KISS_Transmitter sending message of length %d" % len(node_message))
        return  self._send(node_message)
        
        
    
    def _send(self, node_message):
        """
            Send a broadcast message on AX25 
            
            @param node_message: NodeMessage object to send over the network
        """
        dest_callsign = "ALL"
        #logger.debug("Sending payload " + str(len(repr(node_message))) + " long")
        #hexstr = " ".join(["%x" % ord(b) for b in repr(node_message)])
        #logger.debug("Node message bytes = " + hexstr)
        raw = ax25.build_raw_msg(self.call, dest_callsign, repr(node_message))
        kiss = ax25.raw2kiss(raw)
        frame = chr(0xc0)+chr(0x00)+kiss+chr(0xc0) #add KISS framing
        self._flow_control(frame)
        try:
            written = self.ser.write(frame)
            #logger.debug("Bytes written to serial port = %d" % written)
            return written
        except serial.SerialTimeoutException:
            logger.error("Serial write timeout reached")
        except:
            logger.error("Could not send message over KISS mode AX25")


    def _flow_control(self, data):
        """
            Limits speed of writes to avoid overflowing the output buffer
            on the KISS mode TNC
            
            @param data: the data to be transmitted
        """

        now = time.time()
        if now < self.next_send_time:
            wait = self.next_send_time - now
            time.sleep(wait)
            
        #determine next minimum send time based on the number of bits to send and data rate
        self.next_send_time = time.time() + len(data)*8/1200.0
        
        
class AX25_KISS_Receiver(LinkReceiver):
    """
        Define our KISS mode AX25 link protocol receive functions   
    """

    def __init__(self, port='/dev/ttyUSB0'):
        """ 
            Intitilize our Receiver.
        
            @param node_id: provide the local node ID so we can filter 
                    appropriately
            @param port: the serial port for the KISS mode device
        """
        self.port = port
        self.ser = None
        self.buf = ''
        self._connect()

    def _connect(self):
        """
            Connect to the KISS device via the serial port
        """
        try:
            self.ser = serial.Serial(self.port, 9600)
            self.ser.timeout = .01
            logger.debug("Receiver using "+self.port)
        except OSError as err:
            logger.error( err )
            logger.error("Couldn't open serial connection")
        
    def _recv(self):
        """
            Called repeatedly by RxServer.server_forever
            May return None or one or more messages
        """
        #Do once per call
        msgs=[]
        
        # Read from serial device
        if self.ser:
            s = self.ser.read(1000)
            try:
                n = len(s)
            except TypeError:
                n = 0       
        else:
            logger.error("No serial device")
            self._connect()
            time.sleep(5)
            n = 0                
        
        #logger.debug("Received %d bytes" % n)

        # Process received data          
        if n > 0:
            lst = []
            
            w = s.split(chr(0xc0))
            n = len(w)
            
            # No 0xc0 in frame
            if n == 1:
                self.buf += w[0]
        
            # Single 0xc0 in frame
            elif n == 2:
                # Closing 0xc0 found
                if not w[0] == '':
                    # Partial frame continued, otherwise drop
                    lst.append(self.buf + w[0])
                    self.buf = ''
        
                # Opening 0xc0 found
                else:
                    lst.append(self.buf)
                    self.buf = w[1]
        
            # At least one complete frane received
            elif n >= 3:                   
                for i in range(0, n - 1):
                    st = self.buf + w[i]       
                    if not st == '':
                        lst.append(st)
                        self.buf = ''         
                if not w[n - 1] == '':
                    self.buf = w[n - 1]                

            # Loop through received frames
            for p in lst:
                if len(p) == 0:
                    continue                       
                if ord(p[0]) == 0:  #received a data frame
                    #hex_str = " ".join([ "{:02x}".format(ord(c)) for c in p[1:] ])
                    #logger.debug("MSG RAW (HEX): "+hex_str)
                    raw_str = ax25.kiss2raw(p[1:])
                    msg_tuple = ax25.parse_raw_msg(raw_str)
                    if msg_tuple:               
                        strfrom, strto, msg_data, digis = msg_tuple         
                        #logger.debug(msg_data)
                        if len(msg_data) < MESSAGE_HEADER_LEN:
                            logger.error("Did not receive enough "
                                          "data to be a NodeMessage.")
                            #logger.error(`msg_data`)
                            continue
                	    #Convert to Node Message
                        node_msg = NodeMessage(msg_data)
                        if node_msg is not None:      
                            msgs.append((node_msg, strfrom))
                                             
        #return a list of (message, addr) tuples
        if msgs:              
            return msgs
        else:
            return None

         
         
      
