import os
import sys
import psycopg2

# run these commands in courselab sqlite3 mode.

# DATABASE_URL = 'file:reg.sqlite?mode=rwc'

def main():
    try:
        database_url = os.getenv('DATABASE_URL')

        with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                cursor.execute("DROP TABLE IF EXISTS students")

                # programs: enrolled, available, locked
                # program id: P* (append number of 5 digits)
                # assessments: 0 for incomplete, 1 for complete
                # assessment id: a* (append number of 5 digits)

                create_students_table = """ CREATE TABLE students (student_id INTEGER DEFAULT NULL, student_name TEXT DEFAULT NULL, student_email TEXT DEFAULT NULL, P1 TEXT DEFAULT NULL, A1 INTEGER DEFAULT 0)"""

                cursor.execute(create_students_table)
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                cursor.execute("DROP TABLE IF EXISTS programs")

                create_programs_table = """ CREATE TABLE programs (program_id INTEGER DEFAULT NULL, program_name TEXT DEFAULT NULL, description TEXT DEFAULT NULL, initial_availability TEXT DEFAULT NULL)"""

                cursor.execute(create_programs_table)

                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                cursor.execute("DROP TABLE IF EXISTS modules")

                create_modules_table = """ CREATE TABLE modules (module_id INTEGER DEFAULT NULL, program_id INTEGER DEFAULT NULL, module_name TEXT DEFAULT NULL, content_type TEXT DEFAULT NULL, content_link TEXT DEFAULT NULL, module_index INTEGER DEFAULT NULL)"""

                cursor.execute(create_modules_table)

    except Exception as error:
                print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
                sys.exit(1)

if __name__ == '__main__':
    main()
