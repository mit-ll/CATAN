#!/usr/bin/env python
"""
@author Hongyi Hu

© 2015 Massachusetts Institute of Technology
"""
import argparse
import random

import catan.db
from catan.data import NodeMessage

# test data

STATUS_LIST = ['ok', 'injured', 'deceased']

# nodes
def gen_nodes(n, db, start_lat, stop_lat, start_long, stop_long):

    assert n > 0

    cmd = "INSERT INTO catan_nodes VALUES "

    # generate n random nodes, centered around Cambridge
    for i in range(n):
        # random lat, long
        lat = round(random.uniform(start_lat, stop_lat), 6)
        lng = round(random.uniform(start_long, stop_long), 6)

        # node_id, gps_lat, gps_long, gps_acc, path, timestamp
        sql_cmd = cmd + "(%d, %.6f, %.6f, %.6f, %.6f, %.6f)" % (i, lat, lng, 0, 0, 0)
        db._sql(sql_cmd)



# people
def gen_people(n, db, start_lat, stop_lat, start_long, stop_long):
    """
    Generates n people, random male/female ratio between 5 and 90 years of age
    """
    assert n > 0


    # open male first names file
    f = open('dist.male.first','r')
    male_first_names = [name.strip().split()[0] for name in f.readlines()]
    f.close()

    # open female first names file
    f = open('dist.female.first','r')
    female_first_names = [name.strip().split()[0] for name in f.readlines()]
    f.close()

    # open last names file
    f = open('dist.all.last','r')
    family_names = [name.strip().split()[0] for name in f.readlines()]
    f.close()    

    # generate people
    for i in range(n):

        catanDBObj = catan.db.CatanDatabaseObject()

        # bio
        sex = random.randint(0,1)
        if sex == 0: # male
            catanDBObj.person_bio.name_given = male_first_names[random.randint(0,len(male_first_names)-1)]
            catanDBObj.person_bio.sex = 'male'
        else: # female
            catanDBObj.person_bio.name_given = female_first_names[random.randint(0,len(female_first_names)-1)]
            catanDBObj.person_bio.sex = 'female'

        catanDBObj.person_bio.name_family = family_names[random.randint(0,len(family_names)-1)]
        catanDBObj.person_bio.age = random.randint(5,90)

        # message (message, status, location, etc.)
        
        # location
        lat = round(random.uniform(start_lat, stop_lat), 6)
        lng = round(random.uniform(start_long, stop_long), 6)
        
        catanDBObj.person_message.person_message = 'Hi Mom'

        catanDBObj.person_message.status_gps_latitude = lat
        catanDBObj.person_message.status_gps_longitude = lng
        catanDBObj.person_message.status_gps_accuracy = 0
        
        # status
        catanDBObj.person_message.status = STATUS_LIST[random.randint(0,len(STATUS_LIST)-1)]
        catanDBObj.person_message.status_location = 'Test status location'


        # generate a NodeMessage for the database
        # it only cares about the data and source fields, so we can ignore other fields
        nmsg = NodeMessage()
        nmsg.source = random.randint(0,31) # random node 0-31
        nmsg.data = catanDBObj.pack()

        db.update_db(nmsg)

    # Create some random updates
    for i in range(1,n+1):
        update = random.randint(0,1)
        if update == 0:

            catanDBObj = catan.db.CatanDatabaseObject()
            catanDBObj.person_id = i

            # location
            lat = round(random.uniform(start_lat, stop_lat), 6)
            lng = round(random.uniform(start_long, stop_long), 6)
        
            catanDBObj.person_message.person_message = 'Location update 1'
    
            catanDBObj.person_message.status_gps_latitude = lat
            catanDBObj.person_message.status_gps_longitude = lng
            catanDBObj.person_message.status_gps_accuracy = 0

            n = NodeMessage()
            n.source = random.randint(0,31)
            n.data = catanDBObj.pack()

            db.update_db(n)

def populate_db():
    
    db = catan.db.CatanDatabase(0)

    # insert some test nodes
    # for cambridge
    gen_nodes(32, db, 42.354823, 42.368315, -71.114484, -71.084422)
    gen_people(100, db, 42.354823, 42.368315, -71.114484, -71.084422)

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
    pass

if __name__=='__main__':

    populate_db()
