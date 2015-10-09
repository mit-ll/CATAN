"""
    Database operations for services (e.g. request aid, volunteer)

    (c) 2015 Massachusetts Institute of Technology
"""
import catan.globals as G
import catan.db as db
import datetime


class CatanDatabaseService(db.CatanDatabase):

    def get_service_updates(self, service_id):
        """
            Retrieve all of the updates for the given service id

        :param service_id:
        :return:
        """

        sql = """SELECT * FROM db_service_status JOIN db_submitter_info
                 ON db_service_status.submission_id=db_submitter_info.submission_id
                 WHERE service_id = ?
                 ORDER BY timestamp ASC"""

        results = self._sql(sql, [service_id]).fetchall()

        rtn_list = []
        for r in results:
            status = "Unknown"
            if r['service_status'] == G.SERVICE_STATUS.SUBMITTED:
                status = "Submitted"
            elif r['service_status'] == G.SERVICE_STATUS.CANCELED:
                status = "Canceled"
            elif r['service_status'] == G.SERVICE_STATUS.SATISFIED:
                status = "Satisfied"
            elif r['service_status'] == G.SERVICE_STATUS.RESPONSE:
                status = "Response"

            tmp_dict = {
                'service_status': r['service_status'],
                'service_status_text': status,
                'service_comments': r['service_comments'],
                'timestamp': r['timestamp'],
                'timestamp_text': datetime.datetime.fromtimestamp(int(
                    r['timestamp'])).strftime('%b %d, %Y @ %H:%M:%S %z'),
                'service_id': r['service_id']
            }
            rtn_list.append(tmp_dict)

        return rtn_list

    def get_services(self, person_id, service_type):
        """
            Retrieve all of the services of type service_type issued by
            person_id

        :param person_id:
        :return:
        """

        sql = """SELECT * FROM db_services JOIN db_submitter_info
                 ON db_services.submission_id=db_submitter_info.submission_id
                 WHERE person_id = ?
                 AND service_type = ?
                 GROUP BY service_type, service_subtype
                 ORDER BY timestamp DESC"""

        results = self._sql(sql, [person_id, service_type]).fetchall()

        rtn_dict = {}
        for r in results:
            # Get any updates
            updates = self.get_service_updates(r['service_id'])

            inactive = False
            for ru in updates:
                if ru['service_status'] == G.SERVICE_STATUS.SATISFIED or \
                   ru['service_status'] == G.SERVICE_STATUS.CANCELED:
                    inactive = True

            if inactive:
                continue

            # Populate our dict
            rtn_dict[r['service_subtype']] = {
                'updates': updates,
                'timestamp': datetime.datetime.fromtimestamp(int(
                    r['timestamp'])).strftime('%b %d, %Y @ %H:%M:%S %z'),
                'service_id': r['service_id']
            }

        return rtn_dict

    def get_all_services(self):
        """
            Retrieve all of the services that are currently active

        :return:
        """

        sql = """SELECT * FROM db_services
                 JOIN db_submitter_info
                 ON db_services.submission_id=db_submitter_info.submission_id
                 JOIN db_service_status
                 ON db_service_status.submission_id=db_submitter_info.submission_id
                 JOIN db_person_bio
                 ON db_person_bio.person_id=db_services.person_id
                 GROUP BY db_services.person_id, service_type, service_subtype
                 ORDER BY timestamp DESC"""

        results = self._sql(sql, []).fetchall()

        rtn_list = []
        for r in results:
            # Get any updates
            updates = self.get_service_updates(r['service_id'])

            inactive = False
            for ru in updates:
                if ru['service_status'] == G.SERVICE_STATUS.SATISFIED or \
                   ru['service_status'] == G.SERVICE_STATUS.CANCELED:
                    inactive = True

            if inactive:
                continue
            else:
                rtn_list.append(r)

        return rtn_list




class CatanDatabaseServiceObject(db.CatanDatabaseObject):

    def __init__(self, data=None):
        """
            If initialized with data, this will parse the JSON and extract
            the attributes back into our class definitions.

            @param data: JSON string defining this object
        """

        self.person_id = None
        self.origin_node_id = None
        self.submission_id = None
        self.timestamp = None
        self.submitter_id = None
        self.service_id = None

        self.service = db.db_services()
        self.service_status = db.db_service_status()
        self.submitter_info = db.db_submitter_info()

        if data is not None:
            self.__unpack__(data)