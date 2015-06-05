#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    This is our main interface for updating the databse from the web interface
    it simply converts all of the form fields into our database object and 
    writes it to our db_socket to be serviced.
    
    @author: Chad Spensky
"""
# Native
import sys
import os
import datetime
import uuid
import base64

# enable debugging
import cgitb
cgitb.enable()
import logging
logger = logging.getLogger(__name__)

# Web stuff
import cgi
import Cookie

# CATAN
import catan.globals as G
from catan.data import NodeMessage
from catan.db import CatanDatabaseObject, CatanDatabase, DatabaseClient
from catan.comms import TxClient

cookie_value = None

# Send our headers
def send_headers():
    global cookie_value
    
#     print "Content-Type: text/plain;charset=utf-8"

    # Is our cookie already set?
    if "HTTP_COOKIE" in os.environ and "CATAN" in os.environ["HTTP_COOKIE"]:
        cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
        cookie_value = cookie["CATAN"].value
    else:
        # Set our cookie
        cookie_value = str(uuid.uuid1())
        expiration = datetime.datetime.now() + datetime.timedelta(days=120)
        cookie = Cookie.SimpleCookie()
        cookie["CATAN"] = cookie_value
        cookie["CATAN"]["path"] = "/"
        cookie["CATAN"]["expires"] = \
          expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
        
        print cookie.output()
        
    # Print newline to end headers
    print 

# Send our headers
send_headers()

# Get our form object
form = cgi.FieldStorage()

# Initialize our database object
db_obj = CatanDatabaseObject()
DB = CatanDatabase()

# This user is creating their own account
db_obj.user_is_submitter = form.getvalue("user_is_submitter")
db_obj.person_id = form.getvalue("person_id")
db_obj.origin_node_id = form.getvalue("origin_node_id")

# Populate all of our values in our object
for db in db_obj.get_databases():
    for field in db.get_fields():
        v = form.getvalue(field)
        if v is not None and v != "":
            setattr(db,field,v)


# Populate our submitter info
db_obj.submitter_info.cookie = cookie_value
# Any GPS info?
gps_info = form.getvalue("submitter_gps")
if gps_info is not None and gps_info != "":
    (lat, long, acc) = gps_info.split(",")
    db_obj.submitter_info.gps_accuracy = acc
    db_obj.submitter_info.gps_latitude = lat
    db_obj.submitter_info.gps_longitude = long
    
    
# Get our picture info
if "picture_file" in form:
    picture = form['picture_file']
    if picture.filename:
        # Read in our picture data 
        picture_data = base64.b64encode(picture.file.read())
        db_obj.data_picture.picture_data = picture_data

# Create a TxClient
db_client = DatabaseClient()
tx_client = TxClient()

# Send our over the network (This will also update our local database)
# print db_obj.pack()
rtn_data = db_client.send(G.MESSAGE_TYPE.DB_PERSON,`db_obj`)
if rtn_data != 0:
    db_obj_updated = CatanDatabaseObject(rtn_data)
    rtn = tx_client.send(G.MESSAGE_TYPE.DB_PERSON,`db_obj_updated`)
    print rtn
else:
    print 0 
