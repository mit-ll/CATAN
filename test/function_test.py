#!/usr/bin/env python
"""
Functional testing of CATAN backend using randomized model that adds data
to the database for syncing across the network

@author Hongyi Hu

© 2015 Massachusetts Institute of Technology
"""

# Native libs
import argparse
import base64
import logging
import random
import time


# CATAN
import catan.globals as G
import catan.db
from catan.data import NodeMessage


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


# test data
MALE_NAMES_FILE = 'dist.male.first' 
FEMALE_NAMES_FILE = 'dist.female.first'
LAST_NAMES_FILE = 'dist.all.last' 
STATUS_LIST = ['ok', 'injured', 'deceased']


class CatanTester(object):
    """
    Object representing a randomized model for testing CATAN backend.
    """

    def __init__(self, initial_burst, update_interval, update_num, pic, node_id):
        self.initial_burst = initial_burst
        self.update_interval = update_interval
        self.update_num = update_num
        self.node_id = node_id
        self.pic_data = None
        if pic:
            f.open(pic,'rb')
            self.pic_data = base64.b64encode(f.read())
            f.close()

        # open male first names file
        f = open('dist.male.first','r')
        self.male_first_names = [name.strip().split()[0] for name in f.readlines()]
        f.close()

        # open female first names file
        f = open('dist.female.first','r')
        self.female_first_names = [name.strip().split()[0] for name in f.readlines()]
        f.close()

        # open last names file
        f = open('dist.all.last','r')
        self.family_names = [name.strip().split()[0] for name in f.readlines()]
        f.close()

        ## TODO
        # Cambridge GPS coords
        self.start_lat = 42.354823
        self.stop_lat = 42.368315
        self.start_long = -71.114484
        self.stop_long = -71.084422

        # Create TxClient and Database Client
        self.db_client = catan.db.DatabaseClient()
        self.tx_client = catan.db.TxClient()

        # counter
        self.person_counter = 1

    def start(self):
        """
        Creates initial burst of data, then calls self.run()
        """
        # generate initial burst
        for i in xrange(self.initial_burst):
            self.gen_person()
            time.sleep(0.25)

        # run
        self.run()


    def run(self):
        """
        Sends k updates/new people
        every m seconds
        
        where k = [0, self.update_num]
        and m = [0, self.update_interval]
        """
        while True:
            # wait up to self.update_interval seconds
            time.sleep(random.randint(0, self.update_interval))

            # send update
            for i in xrange(random.randint(0, self.update_num)):
                # 50/50 chance of new person or update
                j = random.randint(0,1)
                if (0 == j):
                    self.gen_update()
                else:
                    self.gen_person()

                time.sleep(0.25)


    def gen_person(self):
        """
        Generate random person
        """
        catan_db_obj = catan.db.CatanDatabaseObject()

        # bio
        sex = random.randint(0,1)
        if sex == 0: # male
            catan_db_obj.person_bio.name_given = self.male_first_names[random.randint(0,len(self.male_first_names)-1)]
            catan_db_obj.person_bio.sex = 'male'
        else: # female
            catan_db_obj.person_bio.name_given = self.female_first_names[random.randint(0,len(self.female_first_names)-1)]
            catan_db_obj.person_bio.sex = 'female'

        catan_db_obj.person_bio.name_family = self.family_names[random.randint(0,len(self.family_names)-1)]
        catan_db_obj.person_bio.name_family = catan_db_obj.person_bio.name_family + "-" + str(self.node_id)
            
        catan_db_obj.person_bio.age = random.randint(5,90)

        logger.debug("Generated person %d: %s %s" % (self.person_counter,
                                                     catan_db_obj.person_bio.name_given,
                                                     catan_db_obj.person_bio.name_family))

        # description
        catan_db_obj.person_description.person_description = "Created at <<%d>> \n" % time.time() 
        catan_db_obj.person_description.person_description += "Example description -- average height, average age, etc."

        # contact info
        catan_db_obj.person_contact.street = "Main Street"
        catan_db_obj.person_contact.city = "Cambridge"
        catan_db_obj.person_contact.state = "MA"
        catan_db_obj.person_contact.country= "USA"
        catan_db_obj.person_contact.phone = "555-555-5555"
        catan_db_obj.person_contact.email = "foo@foo.com"

        # location
        lat = round(random.uniform(self.start_lat, self.stop_lat), 6)
        lng = round(random.uniform(self.start_long, self.stop_long), 6)
        
        # Message
        catan_db_obj.person_message.person_message = 'Hi Mom'

        catan_db_obj.person_message.status_gps_latitude = lat
        catan_db_obj.person_message.status_gps_longitude = lng
        catan_db_obj.person_message.status_gps_accuracy = 0

        # status
        catan_db_obj.person_message.status = STATUS_LIST[random.randint(0,len(STATUS_LIST)-1)]
        catan_db_obj.person_message.status_location = 'Test status location'

        # picture data
        if self.pic_data:
            catan_db_obj.data_picture.picture_data = self.pic_data

        
        # send out over network (will also update local database)
        self.send(G.MESSAGE_TYPE.DB_PERSON, catan_db_obj)

        self.person_counter += 1


    def gen_update(self):
        
        # Create random update
        person_id = random.randint(1,self.person_counter)
        person_id = str(person_id) + '-' + str(self.node_id)

        catan_db_obj = catan.db.CatanDatabaseObject()
        catan_db_obj.person_id = person_id

        logger.debug("Updated person_id %s" % person_id)
        
                                                     
        # location
        lat = round(random.uniform(self.start_lat, self.stop_lat), 6)
        lng = round(random.uniform(self.start_long, self.stop_long), 6)
        
        catan_db_obj.person_message.person_message = 'Update at <<%d>>' % time.time()
    
        catan_db_obj.person_message.status_gps_latitude = lat
        catan_db_obj.person_message.status_gps_longitude = lng
        catan_db_obj.person_message.status_gps_accuracy = 0

        # send out over network (will also update local database)
        self.send(G.MESSAGE_TYPE.DB_PERSON, catan_db_obj)


    def send(self, message_type, catan_db_obj):
        # send out over network (will also update local database)
        rtn_data = self.db_client.send(message_type, repr(catan_db_obj))
        if rtn_data != 0:
            db_obj_updated = catan.db.CatanDatabaseObject(rtn_data)
            rtn = self.tx_client.send(message_type, repr(db_obj_updated))
            logger.debug("Sent out : " + str(catan_db_obj))

        


def print_database():
    db = catan.db.CatanDatabase(0)

    cmd = ('SELECT '
           'db_person_bio.person_id, '
           'db_person_bio.origin_node_id, '
           'db_person_bio.name_family, '
           'db_person_bio.name_given, '
           'db_person_bio.age, '
           'db_person_bio.sex, '
           'db_person_messages.submission_id, '
           'db_person_messages.origin_node_id, '
           'db_person_messages.status_gps_latitude, '
           'db_person_messages.status_gps_longitude, '
           'db_person_messages.status_gps_accuracy, '
           'db_person_messages.status, '
           'db_person_messages.status_location, '
           'db_submitter_info.timestamp '
           'FROM db_person_bio '
           'LEFT JOIN db_person_messages ON db_person_messages.person_id = db_person_bio.person_id '
           'LEFT JOIN db_submitter_info ON db_submitter_info.submission_id = db_person_messages.submission_id')
 

    for r in db._sql(cmd).fetchall():
        print r



def main(args):

    catan_tester = CatanTester(args.initial_burst,
                               args.update_interval,
                               args.update_num,
                               args.pic_url,
                               args.node_id)
    
    catan_tester.start()



if __name__=="__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--initial_burst", type=int, dest='initial_burst',
                        default=100,
                        help="Number of people to add in the initial burst of data at time t=0.")
    parser.add_argument("--update_interval", type=int, dest='update_interval',
                        default=300,
                        help="Maximum number of seconds between sending a set of updates.")
    parser.add_argument("--update_num", type=int, dest='update_num',
                        default=5,
                        help="Maximum number of updates to send per burst.")
    parser.add_argument("--picture", action='store', dest='pic_url',
                        help="Picture to use.")
    parser.add_argument("-d", action='store_true', dest='debug',
                        help="Turns debug messages on.")
    parser.add_argument("--node_id", type=int, dest='node_id',
                        help="Node ID used to tag source of entries")
    args = parser.parse_args()

    if args.debug:
        print "* DEBUG Enabled."
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    main(args)
