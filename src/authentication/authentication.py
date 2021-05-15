import urllib.parse

from src.authentication.db_connector import DatabaseConnector


class AuthApi:
    username = None
    password = None

    query = 'SELECT "Username" FROM public."ProfileInformation"'
    #query = "SELECT * FROM ProfileInformation"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def connectToDatabase(self):
        connector = DatabaseConnector()

        connection = connector.connect()

        cursor = connection.cursor()

        self.query = self.query + """ WHERE "Username" = """ + self.value(self.username) + """ AND "Password" = """  + self.value( self.password);
        print("runnin query :", self.query)

        cursor.execute(self.query)

        records = cursor.fetchall()



        connection.close()

        print(records)

        if not records:
            return False
        else:
            return records[0][0] == self.username


    def value(self, value):
        quoted_value =    """'""" + value + """'"""
        print(quoted_value)
        return quoted_value


