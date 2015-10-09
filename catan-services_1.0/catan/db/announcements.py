"""
    Database operations for announcements

    (c) 2015 Massachusetts Institute of Technology
"""
import catan.db as db
import datetime


class CatanDatabaseAnnouncement(db.CatanDatabase):

    def get_announcements(self):
        """
            Retrieve all of the global announcements

        :param service_id:
        :return:
        """

        sql = """SELECT * FROM db_announcements
                 ORDER BY timestamp ASC"""

        results = self._sql(sql, []).fetchall()

        rtn_list = []
        for r in results:
            tmp_dict = dict(r)
            tmp_dict['timestamp_text'] = datetime.datetime.fromtimestamp(int(
                    r['timestamp'])).strftime('%b %d, %Y @ %H:%M:%S %z')

            rtn_list.append(tmp_dict)

        return rtn_list




class CatanDatabaseAnnouncementObject(db.CatanDatabaseObject):

    def __init__(self, data=None):
        """
            If initialized with data, this will parse the JSON and extract
            the attributes back into our class definitions.

            @param data: JSON string defining this object
        """

        self.origin_node_id = None
        self.timestamp = None

        self.announcement = db.db_annoucnments()

        if data is not None:
            self.__unpack__(data)