import sqlite3
import contextlib
import sys

# run these commands in courselab sqlite3 mode.

DATABASE_URL = 'file:reg.sqlite?mode=rwc'

def main():

#! Index on tables? For admin, maybe program id...
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level = None,
        uri = True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:

                create_students_table = """ CREATE TABLE IF NOT EXISTS students (student_id INTEGER DEFAULT NULL, student_name TEXT DEFAULT NULL,
                student_email TEXT DEFAULT NULL, enrollment TEXT DEFAULT NULL, completion TEXT DEFAULT NULL)"""

                cursor.execute(create_students_table)

                create_programs_table = """ CREATE TABLE IF NOT EXISTS programs (program_id INTEGER DEFAULT NULL, program_name TEXT DEFAULT NULL, description TEXT DEFAULT NULL, initial_availability TEXT DEFAULT NULL)"""

                cursor.execute(create_programs_table)

                create_modules_table = """ CREATE TABLE IF NOT EXISTS modules (module_id INTEGER DEFAULT NULL, program_name INTEGER DEFAULT NULL module_name TEXT DEFAULT NULL, content_type TEXT DEFAULT NULL, content_link TEXT DEFAULT NULL, module_index INTEGER DEFAULT NULL)"""

                cursor.execute(create_modules_table)

    except Exception as error:
                print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
                sys.exit(1)

if __name__ == '__main__':
    main()
