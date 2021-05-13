import psycopg2

class DatabaseConnector:
    def connect(self):
        """ Connect to the PostgreSQL database server """
        conn = None
        try:

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="ashankdsouza",
                password="peterparker")

            # create a cursor
            #cur = conn.cursor()

            return conn

            # execute a statement
            #print('PostgreSQL database version:')
            #cur.execute('SELECT version()')

            # display the PostgreSQL database server version
            #db_version = cur.fetchone()
            #print(db_version)

            # close the communication with the PostgreSQL
            #cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
