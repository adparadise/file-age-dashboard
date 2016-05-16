
import psycopg2


class PostgresDatabase:
    """
    A representation of a Postgres database, separating reads from
    writes.
    """

    def __init__(self, config_section_name=None):
        self._config = None
        self._is_read_only = False
        self._connection = None
        self._cursor = None
        self._log = None
        self._config_section_name = config_section_name or 'pg'

    def set_config(self, config):
        self._config = config

    def set_read_only(self, is_read_only):
        self._is_read_only = is_read_only

    def set_log(self, log):
        self._log = log

    def connect(self):
        self._get_connection()

    def close(self):
        self.close_cursor()
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def query_read(self, query, *args):
        cursor = self._get_cursor()
        cursor.execute(query, args)
        results = cursor.fetchall()
        return results

    def query_write(self, query, *args):
        cursor = self._get_cursor()
        cursor.execute(query, args)
        if self._log is not None:
            self._log.debug("query:%s;", cursor.query)
        response_tuple = (cursor.rowcount, cursor.statusmessage)

        return response_tuple

    def query_write_with_results(self, query, *args):
        cursor = self._get_cursor()
        cursor.execute(query, args)
        if self._log is not None:
            self._log.debug("query:%s;", cursor.query)
        response_tuple = (cursor.rowcount, cursor.statusmessage, cursor.fetchall())

        return response_tuple

    def commit(self):
        if self._is_read_only:
            return

        connection = self._get_connection()
        connection.commit()

    def close_cursor(self):
        if not self._cursor:
            return

        self._cursor.close()
        self._cursor = None

    def _get_connection(self):
        if not self._connection:
            self._connection = self._build_connection()

        return self._connection

    def _build_connection(self):
        connection_string = self._build_connection_string()
        connection = psycopg2.connect(connection_string)

        return connection

    def _build_connection_string(self):
        fragments = []

        dbname = self._config.get(self._config_section_name, 'database')
        if dbname:
            fragments.append("dbname=%(dbname)s")

        username = self._config.get(self._config_section_name, 'username')
        if username:
            fragments.append("user=%(username)s")

        hostname = self._config.get(self._config_section_name, 'hostname')
        if hostname:
            fragments.append("host=%(hostname)s")

        port = self._config.get(self._config_section_name, 'port')
        if port:
            fragments.append("port=%(port)s")

        password=self._config.get(self._config_section_name, 'password')
        if password:
            fragments.append("password=%(password)s")

        connection_string = " ".join(fragments) % locals()
        return connection_string

    def _get_cursor(self):
        if not self._cursor:
            connection = self._get_connection()
            self._cursor = connection.cursor()

        return self._cursor

    @staticmethod
    def results_to_dicts(field_names, results):
        return (dict(zip(field_names, result)) for result in results)
