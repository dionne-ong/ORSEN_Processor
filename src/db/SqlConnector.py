import pymysql


class SqlConnector:
    'Connector for ORSEN\'s schema and the server'

    location = "localhost"
    username = "root"
    password = "root"
    schema   = ""

    def __init__(self, schema):
        self.schema     = schema

    @staticmethod
    def getConnection():
        return None

    @staticmethod
    def close(dbConnection):
        dbConnection.close()

# -------------------------------------------------

class SqlConnConcepts(SqlConnector):
    'Connector for ORSEN\'s event chain database'

    schema = "orsen_kb"

    @staticmethod
    def getConnection():
        return pymysql.connect(SqlConnConcepts.location,
                               SqlConnConcepts.username,
                               SqlConnConcepts.password,
                               SqlConnConcepts.schema)

# -------------------------------------------------
