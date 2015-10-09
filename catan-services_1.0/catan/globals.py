"""
    A nice place to keep a bunch of global variables

    (c) 2015 Massachusetts Institute of Technology
"""
import os

TX_DEFAULT_SOCK = "/tmp/catan_tx.sock"
DB_DEFAULT_SOCK = "/tmp/catan_db.sock"

DIR_ROOT = "/opt/catan/"
DIR_EXAMPLES = "examples"
DIR_BINARIES = "bin"
DIR_CONF = "conf"
DIR_SCRIPTS = "scripts"

CONFIG_FILENAME = os.path.join(DIR_ROOT, "conf/catan.conf")

DB_FILENAME = os.path.join(DIR_ROOT, "db/catan.sqlite")
MSG_ID_FILENAME = os.path.join(DIR_ROOT, "db/catan_message_ids.txt")
DB_MSG_FILENAME = os.path.join(DIR_ROOT, "db/catan_messages.sqlite")

METRICS_UPDATE_LOG_FILENAME = os.path.join(DIR_ROOT, "log/metrics_update.log")
METRICS_DBSYNC_LOG_FILENAME = os.path.join(DIR_ROOT, "log/metrics_dbsync.log")
GATEWAY_LOG_FILENAME = os.path.join(DIR_ROOT, "log/gateway.log")

LOG_FILENAME = os.path.join(DIR_ROOT, "log/catan.log")
LOG_DNS = os.path.join(DIR_ROOT, "log/dns.log")
LOG_WEBSERVER = os.path.join(DIR_ROOT, "log/webserver.log")

UNIX_SOCK_MAX_SIZE = 8192

"""
    This class defines our message types.
    
    IMPORTANT: The numbers also assign the priority, priority is given to lower 
                values
                
    Maximum of 255 Message types
"""
class MESSAGE_TYPE:
    
    # Test message (Highest priority for testing purposes)
    TEST = 0
    
    # Broadcast to all users
    BROADCAST_MESSAGE = 5
    
    # Database operations
    DB_PERSON = 6
    DB_SERVICE = 7
    
    # SMS
    SMS_MESSAGE = 8
    
    # Retransmission 
    RETRAMISSION_REQ = 9
    
    # Discovery and routing
    RT_NODE_ANNOUNCEMENT = 10
    RT_GATEWAY_ANNOUNCEMENT = 11
    
    DB_GPS = 12
    
MESSAGE_BROADCAST_ADDRESS = 0
    

RETRANSMIT_INTERVAL = 60 # seconds
RETRANSMISSION_MAX_RECORD_AGE = 60*60*3 # seconds
RETRAMISSION_MESSAGE_TYPES = [MESSAGE_TYPE.DB_PERSON,
                              MESSAGE_TYPE.SMS_MESSAGE]
    
    
MESSAGE_LIST_BROADCAST = [MESSAGE_TYPE.BROADCAST_MESSAGE,
                      MESSAGE_TYPE.RT_GATEWAY_ANNOUNCEMENT,
                      MESSAGE_TYPE.RT_NODE_ANNOUNCEMENT,
                      MESSAGE_TYPE.SMS_MESSAGE]
    
RT_NODE_ANNOUNCEMENT_DELAY = 30 # Seconds


class SERVICE_TYPE:
    REQUEST = 0
    VOLUNTEER = 1

class SERVICE_STATUS:
    SUBMITTED = 0
    CANCELED = 1
    SATISFIED = 2
    RESPONSE = 3

class SERVICE_REQUEST_TYPE:
    DECEASED = 0
    WATER = 1
    FOOD = 2
    SHELTER = 3
    CLEANUP = 4
    FUEL = 5

class SERVICE_VOLUNTEER_TYPE:
    TRANSLATOR = 0
    GUIDE = 1
    LABORER = 2
    COUNSELER = 3
    RESCUER = 4
    TRANSPORTATION = 5


# UDP Specific settings
# UDP Broadcast Addr needs to be '10.255.255.255' for the linksys
UDP_MAX_SIZE = 65507 # bytes
UDP_DEFAULT_PORT = 11113
UDP_DEFAULT_INTERFACE = "eth0" # currently unimplemented
UDP_BROADCAST_ADDRESS = '10.255.255.255'  # '<broadcast>'
UDP_TX_LIMIT = 0 # no limit 1024*10 # bytes/second

#AX25 Specific Settings
AX25_MAX_SIZE = 200 #bytes
