#--------------------------------------------------------------------
# database.py (deals with selecting from database)
# Authors: Liz Garcia, Matthew Higgins Iati
#--------------------------------------------------------------------
import sqlite3
import contextlib
import sys

# run these commands in courselab sqlite3 mode.

DATABASE_URL = 'file:reg.sqlite?mode=rwc'

def main():

    try:
        with sqlite3.connect(DATABASE_URL, isolation_level = None,
        uri = True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:

                create_students_table = ''' CREATE TABLE IF NOT EXISTS
                students (student_id INTEGER, student_name TEXT,
                student_email TEXT, enrollment TEXT, completion TEXT)'''

                cursor.execute(create_students_table)

                create_programs_table = ''' CREATE TABLE IF NOT EXISTS
                  programs (program_id INTEGER, program_name TEXT,
                  description TEXT, initial_availability TEXT)'''

                cursor.execute(create_programs_table)

                create_modules_table = ''' CREATE TABLE IF NOT EXISTS
                  modules (module_id INTEGER, program_name INTEGER,
                  module_name TEXT, content_type TEXT, content_link
                  BLOB, module_index INTEGER)'''

                cursor.execute(create_modules_table)

    except Exception as error:
                print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
                sys.exit(1)

if __name__ == '__main__':
    main()
