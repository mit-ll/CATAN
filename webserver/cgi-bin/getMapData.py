#!/usr/bin/python
"""

@author Hongyi Hu
© 2015 Massachusetts Institute of Technology
"""
import json
import os
import sys

# enable debugging
import cgitb
cgitb.enable()

# web stuff
import cgi

# CATAN
import catan.db

# do a database lookup
    
result = {}
result['nodes'] = []
result['people'] = []

db = catan.db.CatanDatabase(-1)

# nodes
cmd = "SELECT node_id, gps_latitude, gps_longitude FROM db_node_info GROUP BY node_id ORDER BY timestamp DESC "
for node_info in db._sql(cmd).fetchall():
    r = {}
    r['node_id'] = node_info[0]
    r['gps_latitude'] = node_info[1]
    r['gps_longitude'] = node_info[2]

    result['nodes'].append(r)

# people
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

# dictionary
d = {}

for person in db._sql(cmd).fetchall():

    # check if we already have this person in the dictionary
    person_id = person[0]
    
    if person_id in d:

        # potential update
        
        update = {}
        update['submission_id'] = person[6]
        update['origin_node_id'] = person[7]
        update['location_gps_latitude'] = person[8]
        update['location_gps_longitude'] = person[9]
        update['location_gps_accuracy'] = person[10]
        update['status'] = person[11]
        update['status_location'] = person[12]
        update['timestamp'] = person[13]


        # ignore if just a message and no update to
        # location or status
        if (not update['location_gps_latitude'] and
            not update['location_gps_longitude'] and
            not update['location_gps_accuracy'] and
            not update['status'] and
            not update['status_location']):

            continue

        d[person_id]['updates'].append(update)

        # update the latest status if this timestamp is later
        if update['timestamp'] > d[person_id]['latest_timestamp']:
            d[person_id]['latest_timestamp'] = update['timestamp']

            # only update location if there is an update
            # don't want to overwrite good data if there is no
            # update

            if update['location_gps_latitude']:
                d[person_id]['location_gps_latitude'] = update['location_gps_latitude']
            if update['location_gps_longitude']:
                d[person_id]['location_gps_longitude'] = update['location_gps_longitude']
            if update['location_gps_accuracy']:
                d[person_id]['location_gps_accuracy'] = update['location_gps_accuracy']
            if update['status']:
                d[person_id]['status'] = update['status']
            if update['status_location']:
                d[person_id]['status_location'] = update['status_location']

    else:
        # add all the fields

        # basic info
        p = {}
        p['person_id'] = person[0]
        p['origin_node_id'] = person[1]
        p['name_family'] = person[2]
        p['name_given'] = person[3]
        p['age'] = person[4]
        p['sex'] = person[5]
        
        # latest status
        p['latest_timestamp'] = person[13]
        p['location_gps_latitude'] = person[8]
        p['location_gps_longitude'] = person[9]
        p['location_gps_accuracy'] = person[10]
        p['status'] = person[11]
        p['status_location'] = person[12]

        # updates
        p['updates'] = []

        d[person_id] = p


# add people
result['people'] = d.values()

# Return result

print 'Content-Type: application/json\n\n' + json.dumps(result)    
