"""
    Database operations for GPS

    (c) 2015 Massachusetts Institute of Technology
"""
import catan.db as db

class CatanDatabaseGPS(db.CatanDatabase):

    def get_recent_gps(self, timestamp=None):
        """
            Retrieve all of the updates for the given service id

        :param service_id:
        :return:
        """

        sql = """SELECT * FROM db_node_info
                 GROUP BY node_id
                 ORDER BY timestamp ASC"""

        results = self._sql(sql, []).fetchall()

        return results

    def get_last_gps(self, node_id):
        """
            Get the most recent successful GPS coordinate for Node ID

        :param node_id:
        :return:
        """
        sql = """SELECT * FROM db_node_info
                 WHERE node_id = ?
                 ORDER BY timestamp ASC
                 LIMIT 1"""

        result = self._sql(sql, [node_id]).fetchone()

        return result
