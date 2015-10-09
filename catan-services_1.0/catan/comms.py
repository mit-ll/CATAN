"""
    All of the classes which handle our TX communication for our CATAN nodes.
    
    (c) 2015 Massachusetts Institute of Technology
"""
# Native
import multiprocessing
import os
import SocketServer
import heapq
import socket
import time
import logging
import math
import copy
import json
logger = logging.getLogger(__name__)

# CATAN
from catan.data import NodeMessage
from comms_db import RetransmissionDatabase
import catan.globals as G

# Main queue used to support multithread support
TX_QUEUE = multiprocessing.Queue()
RX_QUEUE = multiprocessing.Queue()

# Constansts
MESSAGE_HEADER_LEN = len(NodeMessage())


class TxScheduler(multiprocessing.Process):
    """
        This scheduler will take care of prioritization of messages to send over
        our RF link
    """
    
    MESSAGE_ID = {}
    
    def __init__(self, 
                 tx_backlink, 
                 node_id, 
                 node_dict,
                 gateway_id_obj,
                 db_retransmission=None):
        """
            Initialize our scheduler with the tx_backlink object to actually send 
            the data.
        
            @param tx_backlink: Backlink used to transmit data (Likely RF)
            @param node_id: Keep track of Node ID for RX loopback handling
            @param node_dict: Dict of all of the paths to nodes in our system
            @param gateway_id_obj: Threadsafe ID of this node's gateway node
            @param db_retransmission: Inteface to our databse to handle 
                                        re-transmissions
        """
        self.backlink = tx_backlink
        self.my_node_id = node_id
        self.node_dict = node_dict
        self.gateway_id_obj = gateway_id_obj
        
        self._db_sent = db_retransmission
        
        multiprocessing.Process.__init__(self)
    
    
    def _update_routing(self, node_message):
        """
            The function will update all of our routing headers.
            
            NOTE: We assume that: (visited = path = 0) => initiator
        """
        gateway_id = self.gateway_id_obj.value
        node_dict = self.node_dict
        
        # Is this an intial message, or are we just updating the status
        if node_message.visited == 0 and node_message.path == 0:
            
            # All packets are broadcast
            # Set all of the bits to be one in our destination bitmask
            node_message.path = 0xFFFFFFFF
             
            # Is an explicit destination set?
            if node_message.destination in node_dict:
                node_message.path = node_dict[node_message.destination]
        
        # Always mark ourselves in the visited
        node_message.visited |= (1 << self.my_node_id)
        
        # Clear our bit if it was set
        node_message.path ^= (node_message.path & 1 << self.my_node_id)  
        
    
    def _update_message(self, node_message):
        """
            This function will ensure that all of our fields in the message 
            header are populated appropriately.
        """     
        # Only handle messages in our format
        if not isinstance(node_message,NodeMessage):
            logger.error("Message does not seem be of type NodeMessage.  Aborting transmit.")
            return False
        
        # Update our routing and destination
        self._update_routing(node_message)

        # Set our source my_node_id
        node_message.source = self.my_node_id
        
        # Ensure we always have a proper length
        if node_message.data is None:
            node_message.data = ""
        node_message.length = len(node_message.data)
        
        # Update our node ID, but allow overriding
        if node_message.id is None or node_message.id == 0:
            if node_message.type in TxScheduler.MESSAGE_ID:
                node_message.id = TxScheduler.MESSAGE_ID[node_message.type]
                TxScheduler.MESSAGE_ID[node_message.type] += 1
            else:
                node_message.id = 1
                TxScheduler.MESSAGE_ID[node_message.type] = 2
        
        
        
        return True
    
    
    def run(self):
        """
            Simply consume packages from our queue, prioritize them and try to
            forward out on our RF link.
        """
        
        priority_queue = []
        while True:
            
            # Receive all outstanding messages and prioritize them
            while not TX_QUEUE.empty() or len(priority_queue) == 0:
                
                # Get our message from the queue
                msg = TX_QUEUE.get()
                logger.debug("Scheduler got message")
                 
                if not self._update_message(msg):
                    continue

                # Local message or remote?
                if msg.destination == self.my_node_id:
                    logger.debug("RX loopback message.")
                    
                    # Update our path to ensure we accept it
                    msg.path |= 1 << self.my_node_id 
                    RX_QUEUE.put( (msg, ('localhost', 'LOOPBACK')) )
                else:
                    logger.debug("Message placed in heap")
                    heapq.heappush(priority_queue, (msg.type, msg))

            # Send the highest priority item to our RF TX
            send_msg = heapq.heappop(priority_queue)[1]
            
            # Log every message that we send
            if self._db_sent is not None:
                self._db_sent.store_sent_message(send_msg)
            
            # Send the message over our backlink
            logger.debug("Sending message using backlink")
            logger.debug(send_msg)
            self.backlink.send(send_msg)
        
       
class TxFragmentingScheduler(TxScheduler):
    """
        This scheduler will take care of prioritization of messages to send over
        our RF link
        It fragments messages into chunks no larger than 
    """
        
    def run(self):
        """
            Simply consume packages from our queue, prioritize them and try to
            forward out on our RF link.
        """
        
        priority_queue = []
        while True:
            
            # Receive all outstanding messages and prioritize them
            while not TX_QUEUE.empty() or len(priority_queue) == 0:
                
                # Get our message from the queue
                msg = TX_QUEUE.get()
                logger.debug("Fragmenting Scheduler got message")
                
                #fragment messages as necessary
                fmsg_list = self._fragment(msg)
                
                #for each fragment do 
                for fmsg in fmsg_list:
                    #logger.debug("Sending Fragmented message"+" of type %s" % type(fmsg) )
                    #the same thing as before
                    if not self._update_message(fmsg):
                        continue

                    # Local message or remote?
                    if fmsg.destination == self.my_node_id:
                        logger.debug("RX loopback message.")
                        
                        # Update our path to ensure we accept it
                        fmsg.path |= 1 << self.my_node_id 
                        RX_QUEUE.put( (fmsg, ('localhost', 'LOOPBACK')) )
                    else:
                        logger.debug("Message placed in heap")
                        heapq.heappush(priority_queue, (fmsg.type, fmsg))

            # Send the highest priority item to our RF TX
            send_msg = heapq.heappop(priority_queue)[1]
            
            # Log every message that we send
            if self._db_sent is not None:
                self._db_sent.store_sent_message(send_msg)
            
            # Send the message over our backlink
            logger.debug("Sending message using backlink")
            logger.debug(send_msg)
            self.backlink.send(send_msg)
            
            
    def _fragment(self, orig_msg):
        """
            Split data across multiple Node message as needed
        """
        size = G.AX25_MAX_SIZE
        data = orig_msg.data
        if not data:
            #if there is no data in the message return the original message
            return [orig_msg]
            
        if orig_msg.frag_num > 1:    
            #if the message has already been fragmented return the original message
            logger.debug("Previously fragmented message - keeping existing frag_id and frag_num")
            return [orig_msg]
                       
        frag_num = int(math.ceil(len(data)/float(size)))
        data_chunks = [(data[i*size:(i+1)*size], i) for i in range(0, frag_num)]
        logger.debug("Splitting data over %d packets" % frag_num)
        logger.debug("Original data is:")
        logger.debug(orig_msg.data)
        #print "Splitting messages over %d packets" % frag_num
        #print data_chunks
        
        msg_list = []
        
        for data, frag_id in data_chunks:
            # Define a node message
            msg = copy.copy(orig_msg)
            msg.data = data
            msg.length = len(msg.data)
            msg.frag_id = frag_id
            msg.frag_num = frag_num
            msg_list.append(msg)
            #logger.debug("split %d of %d (msg id not yet assigned)" % (frag_id, frag_num) )
            #logger.debug(msg)
            #logger.debug(msg.data)
            
        return msg_list
        
        
class TxHandler(SocketServer.BaseRequestHandler):
    """
         This class is our basic handler for all inputs
    """
    
    def handle(self):
        """
            This function handles any inputs to our tx socket
        """
        sock = self.request
        
        logger.debug("Handler got message, forwarding to scheduler...")
        
        # Receive our header
        msg = NodeMessage()
        header = sock.recv(len(msg))
        
        # Receive our data
        msg._unpack(header)
        if msg.length > 0:
            msg.data = sock.recv(msg.length)
        
        # Forward data along to our scheduler
        TX_QUEUE.put(msg)
      
       
      
class TxServer(multiprocessing.Process):
    """
        This is our main TX server for CATAN.  It will open a unix socket at 
        the given location and listen.
        
        It is multithreaded and will receive as many packets as we throw at it.
        It then fowards these to our scheduler to be sent over our backend
    """
    
    def __init__(self,
                 socket_name=G.TX_DEFAULT_SOCK):
        """
            Initialize our socket
            
            @param socket_name: Filename of UNIX socket to open for TX 
            transmissions
        """
        
        # Store our socket file name
        self.socket_name = socket_name
        if os.path.exists(self.socket_name):
            try:
                os.unlink(self.socket_name)
            except:
                logger.error("Could not delete %s, socket creation will fail."%
                             self.socket_name)
                
        
        
        # Setup our server
        self.server = SocketServer.UnixStreamServer(socket_name,TxHandler)
        
        # IMPORTANT: Allow everyone to write to the socket
        os.chmod(socket_name, 0777)
        
        multiprocessing.Process.__init__(self)
        
        
    def __del__(self):
        """ Try to cleanup our socket """
        os.unlink(self.socket_name)

                
    def serve_forever(self):
        """
            Just a wrapper around a SocketServer
        """
    
        # Start our server
        self.server.serve_forever()
        
        
    def run(self):
        self.serve_forever()
        
        

class TxClient:
    """
        This class is the API to properly interact with our TXServer which will
        use the scheduler etc.
    """
    
    def __init__(self,server_name=G.TX_DEFAULT_SOCK):
        """
            Initialize with the filename of our UNIX socket
            
            @param server_name: Name of our TX socket name
        """

        self.server_name = server_name
    
    
    def _send(self, node_message):
        """
            Send a NodeMessage to the UNIX socket to be scheduled and sent over
            our backlink.
        """
        
        # Only handle messages in our format
        if not isinstance(node_message,NodeMessage):
            logger.error("Message does not seem be of type NodeMessage.  Aborting sending.")
            return False
        
        try:
            # Create a socket (SOCK_STREAM means a TCP socket)
            self.SOCK = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
            # Connect to server and send data
            self.SOCK.connect(self.server_name)
            
            # Send the message
            rtn = self.SOCK.sendall(`node_message`)
            
        except:
            logger.error("Failed to send message to our TX server.")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.SOCK.close()
            
        return True

    def send(self, message_type, data="", destination=G.MESSAGE_BROADCAST_ADDRESS):
        """
            Craft a Node message and send it over our local UNIX socket
        """
        # Define a node message
        msg = NodeMessage()
        
        msg.source = 0                  # Set by lower-level protocol
        msg.my_node_id = 0              # Set by lower-level protocol
        msg.path = 0                    # Will be populated by our underlying
                                        # routing algorithm
        msg.visited = 0                 # Always starts at 0
        # Must fill these in
        msg.type = message_type
        msg.data = data
        msg.destination = destination
        msg.frag_id = 0
        msg.frag_num = 1
        
        # Set the Length
        msg.length = len(msg.data)
        
        return self._send(msg)

        
class FragmentReassembler:
    """
        Keeps track of fragmented packets and reassembles them into a
        node packet with the complete data payload
    """ 
    def __init__(self):
        """
            Initializes a dictionary to keep track of incomplete messages
        """
        self.messages = dict()
        
    def reassemble_or_add(self, node_message):
        """
            Public interface for the class
            
            Returns a reassembled NodeMessage if possible
            or None if not all the fragments have been received
        """
        if node_message.frag_num == 1:
            return node_message
            
        self._add_fragment(node_message)  
            
        if self._is_message_complete(node_message):
            return self._reassemble_msg(node_message)
        else: 
            return None
            
    def _add_msg_dict(self, node_message):
        """
            Creates a new dict containing the first NodeMessage
            of a fragment and adds that dict to self.messages
        """   
        start_id = node_message.id - node_message.frag_id
        msg_key = (node_message.source, node_message.type, start_id)
        self.messages[msg_key] = {node_message.frag_id: node_message}
            
    def _get_msg_dict(self, node_message):
        """
            Gets the dict of fragments in self.messages that correspond
            to the given NodeMessage
        """
        start_id = node_message.id - node_message.frag_id
        msg_key = (node_message.source, node_message.type,  start_id)        
        if msg_key in self.messages:
            #add the fragment to the corresponding mgs_dict in messages
            return self.messages[msg_key]
        else:
            return None
    
    def _pop_msg_dict(self, node_message):
        """
            Gets the dict of fragments in self.messages that correspond
            to the given NodeMessage and pops the dict from self.messages
        """
        start_id = node_message.id - node_message.frag_id
        msg_key = (node_message.source, node_message.type,  start_id)
        return self.messages.pop(msg_key) 
            
    def _add_fragment(self, node_message):
        """
            Adds an incoming fragment to the correct message dict
            creating a new entry in self.messages if necessary
        """
        logger.debug("adding a fragment")
        msg_dict = self._get_msg_dict(node_message)
        if msg_dict:
            #add the fragment to the corresponding mgs_dict in messages
            msg_dict[node_message.frag_id] = node_message
        else:
            #create a new entry in messages
            self._add_msg_dict(node_message)

    def _is_message_complete(self, node_message):
        """
            Checks if all the fragments have been received 
        """
        msg_dict = self._get_msg_dict(node_message)
        return True if len(msg_dict) == node_message.frag_num else False

    def _reassemble_msg(self, node_message):
        """
            Reassembles the fragments associated with the given 
            NodeMessage and returns a single complete NodeMessage
        """
        logger.debug("reassembling a complete message")
        msg_dict = self._pop_msg_dict(node_message)
        msg_list = msg_dict.items()
        msg_list.sort()
        data = ''.join([msg[1].data for msg in msg_list])
        node_message.data = data
        node_message.length = len(data)
        node_message.frag_id = 0
        node_message.frag_num = 1
        node_message.id = None
        self._check_msg(node_message, msg_list)
        self._print_queue_status()
        return node_message
        
    def _check_msg(self, node_message, msg_list):
        """
            Checks that the NodeMessage contains valid data
        """
        try:
            class_dict = json.loads(node_message.data)
            return True
        except:
            print "ERROR parsing reassembled message"
            import traceback
            traceback.print_exc()
            print "Reassembled message:"
            print node_message.data
            print "Original fragments:"
            for msg in msg_list:
                print msg[1].data
            return False
        
    def _print_queue_status(self):
        """
            Logs the number of partial messages that remain in self.messages
        """
        logger.debug("%d partial messages in the queue" % len(self.messages))
        for msg_key, msg_dict in self.messages.items():
            logger.debug(msg_key)
            for frag_key, frag in msg_dict.items():
                logger.debug(frag.data)
            
class RxServer(multiprocessing.Process):
    
    def __init__(self,rx_backlink,node_id):
        """
            Intitilize our Receiver with the appropriate backlinks.  Both RX 
            and TX are required for forwarding.
        
            @param rx_backlink:  Backlink receiver object
            @param node_id: provide the local node ID so we can filter 
                    appropriately
        """
        self.rx_backlink = rx_backlink
        self.my_node_id = node_id
        
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
        
        
        while True:
            logger.debug("Receiving data...")
            msgs = self.rx_backlink.recv()
            logger.debug("Got %d messages from backlink" % len(msgs))
            for msg in msgs:
                # Filter messages from our self.  (Pretty likely with RF)
                if msg[0].source == self.my_node_id:
                    logger.debug("Got message from myself, ignoring.")
                    continue

                # Add to our RX queue
                RX_QUEUE.put(msg)
            
    def run(self):
        self.serve_forever()
      
   
class ReTransmitServer(multiprocessing.Process):
    """
        This server continously scans our retransmission database and will
        send messages for outstanding retransmission requests
    """
    def __init__(self, db):
        
        self.db = db
        self.tx_client = TxClient()
        
        multiprocessing.Process.__init__(self)
        
        
        
    def run(self):
        
        while True:
            
            retrans = self.db.get_retransmissions()
            
            logger.debug("Sending %d retransmission request packets."%
                         len(retrans))
            
            for node_id in retrans:
                data = retrans[node_id]
                self.tx_client.send(G.MESSAGE_TYPE.RETRAMISSION_REQ, 
                                    `data`,
                                    destination=node_id)
            
            time.sleep(G.RETRANSMIT_INTERVAL)
