"""
    Database operations for node information

    (c) 2015 Massachusetts Institute of Technology
"""
import catan.db as db

class CatanDatabaseNodeObject(db.CatanDatabaseObject):

     def __init__(self, data=None):
        """
            If initialized with data, this will parse the JSON and extract
            the attributes back into our class definitions.

            @param data: JSON string defining this object
        """
        self.origin_node_id = None
        self.submission_id = None
        self.timestamp = None

        self.node_info = db.db_node_info()
        self.submitter_info = db.db_submitter_info()

        if data is not None:
            self.__unpack__(data)