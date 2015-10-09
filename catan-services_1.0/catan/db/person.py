"""
    Database operations for persons

    (c) 2015 Massachusetts Institute of Technology
"""
import catan.db as db

class CatanDatabasePerson(db.CatanDatabase):

    def get_recent_fields_for_person(self, database_name, person_id):
        """
            Returns a dictionary containing the most recently updated values
            in each field of the selected database for the given person_id.

            database_name should NOT be derived from user supplied values.
        """

        SQL = '''SELECT *
                 FROM %s AS in_db
                 JOIN db_submitter_info AS sub
                    ON sub.submission_id=in_db.submission_id
                 WHERE sub.submission_id=in_db.submission_id
                 AND sub.origin_node_id=in_db.origin_node_id
                 AND in_db.person_id = ?
                 ORDER BY sub.timestamp DESC'''

        SQL = SQL % database_name

        results = self._sql(SQL, [person_id])

        data = results.fetchall()

        ret_dict = {}
        if data:
            columns = data[0].keys()
            for row in data:
                for key, val in zip(columns, row):
                    if key not in ret_dict:
                        ret_dict[key] = val

                    if key in ret_dict and ret_dict[key] is None:
                        ret_dict[key] = val
        else:
            ret_dict = None

        return ret_dict

    def get_person_info(self, person_id):
        """
            Returns a dictionary containing the most recent values for all
            the fields associated with a given person id.
        """
        summary_dict = {}
        databases = ['db_person_bio', 'db_person_contact',
                     'db_person_description']
        for db in databases:
            temp_dict = self.get_recent_fields_for_person(db, person_id)
            if temp_dict:
                summary_dict.update(temp_dict)

        return summary_dict

    def get_pictures(self, person_id):
        """
        Returns all of the pictures associated with the person id
        :param person_id:  person_id in database
        :return: List of picture filenames
        """

        SQL = '''SELECT * FROM db_pictures
                JOIN db_person_pictures
                JOIN db_submitter_info
                WHERE db_pictures.picture_id=db_person_pictures.picture_id
                AND db_pictures.origin_node_id=db_person_pictures.origin_node_id
                AND db_submitter_info.origin_node_id=db_person_pictures.origin_node_id
                AND db_submitter_info.submission_id=db_person_pictures.submission_id
                AND person_id = ?
                ORDER BY db_submitter_info.timestamp DESC'''

        results = self._sql(SQL, [person_id]).fetchall()

        results_list = [r[0] for r in results]

        return results_list

    def get_person_ids(self):
        """
            Returns a list of all person_id entries in the database
        """
        SQL = '''SELECT person_id
                 FROM db_person_bio'''

        results = self._sql(SQL, []).fetchall()

        results_list = [r[0] for r in results]

        return results_list

    def get_messages_by_person(self, person_id):
        """
            Returns a list of dictionaries.  Each dictionary contains the fields
            specified below describing the contents of one person message.
        """
        # define the data items that will be retreived
        variables = ['person_id', 'origin_node_id', 'status', 'status_location',
                     'status_gps_latitude', 'status_gps_longitude', 'status_gps_accuracy',
                     'person_message', 'imsi', 'gps_latitude', 'gps_longitude', 'gps_accuracy',
                     'timestamp', 'sub_name_family', 'sub_name_given', 'sub_age', 'sub_sex',
                     'submission_id', 'submitter_id']

        # the selected fields should correspond (in order) the variables above
        SQL = '''SELECT messages.person_id, messages.origin_node_id, status, status_location,
                        status_gps_latitude, status_gps_longitude, status_gps_accuracy,
                        person_message, imsi, gps_latitude, gps_longitude, gps_accuracy,
                        timestamp, bio.name_family, bio.name_given, bio.age, bio.sex,
                        sub.submission_id, sub.submitter_id
                 FROM db_person_messages AS messages
                 JOIN db_submitter_info AS sub
                    ON sub.submission_id=messages.submission_id
                    AND sub.origin_node_id=messages.origin_node_id
                    LEFT JOIN db_person_bio AS bio
                    ON bio.person_id=sub.submitter_id
                WHERE messages.person_id = ?
                ORDER BY sub.timestamp DESC'''

        # execute the query
        results = self._sql(SQL, [person_id]).fetchall()

        # put the results in list of dictionaries
        result_dicts = [{name: value for name, value in
                         zip(variables, result)} for result in results]

        return result_dicts

    def get_person_name(self, person_id):
        """
            Just return the name of the person assosciated with that PID.

        :param person_id: person ID in the database
        :return: {'name_family', 'name_given'}
        """

        SQL = '''SELECT name_family, name_given
                 FROM db_person_bio
                 WHERE person_id = ?
                 LIMIT 1'''

        # execute the query
        result = self._sql(SQL, [person_id]).fetchone()

        return {'name_family' : result['name_family'],
                'name_given': result['name_given']}

    def get_search_results(self, name_family, name_given):
        """
        Return the results of a person search
        :param name_family: Family Name
        :param name_given: Given Name
        :return: List of persons matching this criteria
        """

        name_family = '%'+name_family+'%'
        name_given = '%'+name_given+'%'

        SQL = '''SELECT * FROM db_person_bio WHERE name_given LIKE ? and
        name_family LIKE ?'''

        # execute the query
        results = self._sql(SQL, [name_given, name_family]).fetchall()

        return results

class CatanDatabasePersonObject(db.CatanDatabaseObject):

     def __init__(self, data=None):
        """
            If initialized with data, this will parse the JSON and extract
            the attributes back into our class definitions.

            @param data: JSON string defining this object
        """

        self.person_id = None
        self.user_is_submitter = None
        self.origin_node_id = None
        self.submission_id = None
        self.picture_id = None
        self.timestamp = None
        self.submitter_id = None

        self.node_info = db.db_node_info()
        self.submitter_info = db.db_submitter_info()
        self.person_bio = db.db_person_bio()
        self.person_description = db.db_person_description()
        self.person_contact = db.db_person_contact()
        self.person_picture = db.db_person_pictures()
        self.person_links = db.db_person_links()
        self.person_message = db.db_person_messages()

        self.data_picture = db.db_pictures()

        if data is not None:
            self.__unpack__(data)