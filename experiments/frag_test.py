# © 2015 Massachusetts Institute of Technology
import string
import random
from catan.comms import TxClient, TxFragmentClient, FragmentReassembler
import catan.globals as G
import logging
logger = logging.getLogger(__name__)

messageList = []

def string_generator(size=100, chars = string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class TxClientStubbed(TxFragmentClient):
    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.msg_id_counter = 0
        
    def _send(self, node_message):
        node_message.id = self.msg_id_counter
        self.msg_id_counter += 1
        print "Sending a message..."
        print node_message
        print "data = ", node_message.data
        messageList.append(node_message)
        return True

def main():
    #create objects
    G.AX25_MAX_SIZE = 40 #change max payload size to faciliate testing
    tx_client = TxClientStubbed(server_name='') #use a stubbed version of the TXFragmentClient
    #tx_client.send(G.MESSAGE_TYPE.RT_GATEWAY_ANNOUNCEMENT, data="One Fragment Message")
    #tx_client.send(G.MESSAGE_TYPE.RT_GATEWAY_ANNOUNCEMENT, data= (40*'a' + 40*'b' + 40*'c'))
    teststrings = [string_generator(int(random.uniform(10, 200))) for _ in range(5)]
    for s in teststrings:
        tx_client.send(G.MESSAGE_TYPE.RT_GATEWAY_ANNOUNCEMENT, data=s)

    print "\nThere are %d messages in the list\n" % len(messageList)
    
    # Set our fragment reassembler
    reassembler = FragmentReassembler()
    
    for node_message in messageList:
        # Is this message part of a multi-fragment message?
        # try to get the complete message
        node_message = reassembler.reassemble_or_add(node_message)
        if node_message:
            print "Complete message"
            test_string = teststrings.pop(0)
            assert(test_string == node_message.data)
            print node_message
            print "data = ", node_message.data
            
        else:
            #this was just a fragment, need to wait for the rest of the message
            print "Message Fragment"
            continue
    
    print "Test complete"

if __name__ == "__main__":
    main()
