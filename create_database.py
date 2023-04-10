import os
import queue
import sys
import psycopg2

# run these commands in courselab sqlite3 mode.

def _put_connection(conn):
    _connection_pool.put(conn)

# _database_url = os.getenv('DATABASE_URL')
_database_url = 'postgres://oea_user:KTYMB7UGGi1I8wXjXAFr3vvqNbl5lN4X@dpg-cgp3bg0u9tun42rpj98g-a.oregon-postgres.render.com/oea'
_connection_pool = queue.Queue()

def _get_connection():
    try:
        conn = _connection_pool.get(block=False)
    except:
        conn = psycopg2.connect(_database_url)
    return conn

def _put_connection(conn):
    _connection_pool.put(conn)

def main():
    print(_database_url)
    connection = _get_connection()
    try:
        #database_url = os.getenv('DATABASE_URL')

        #conn = psycopg2.connect("dbname=oea user=rmd password=xxx")

        # with conn as connection:
        # with psycopg2.connect(database_url) as connection:

        with connection.cursor() as cursor:
            print("connection made")
            cursor.execute("DROP TABLE IF EXISTS students;")

            cursor.execute("DROP TABLE IF EXISTS users;")

            # programs: enrolled, available, locked
            # program id: P* (append number of 5 digits)
            # assessments: 0 for incomplete, 1 for complete
            # assessment id: a* (append number of 5 digits)

            create_users_table = """ CREATE TABLE users (user_id INTEGER GENERATED ALWAYS AS IDENTITY, user_name TEXT DEFAULT NULL, user_email TEXT DEFAULT NULL, user_status TEXT);"""
            #! do not add P1 and A1 columns because that should be done by admin.


            cursor.execute(create_users_table)
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            cursor.execute("DROP TABLE IF EXISTS programs;")

            create_programs_table = """ CREATE TABLE programs (program_id TEXT, program_name TEXT DEFAULT NULL, description TEXT DEFAULT NULL, program_availability TEXT DEFAULT 'none');"""

            cursor.execute(create_programs_table)

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

            cursor.execute("DROP TABLE IF EXISTS modules;")

            create_modules_table = """ CREATE TABLE modules (module_id TEXT, program_id TEXT, module_name TEXT, content_type TEXT, content_link TEXT, module_index INTEGER);"""

            cursor.execute(create_modules_table)

    except Exception as error:
                print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
                sys.exit(1)
    finally:
        _put_connection(connection)

if __name__ == '__main__':
    main()
