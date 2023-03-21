import os
import sys
import psycopg2

# run these commands in courselab sqlite3 mode.

# DATABASE_URL = 'file:reg.sqlite?mode=rwc'

def main():
    try:
        database_url = os.getenv('DATABASE_URL')

        conn = psycopg2.connect("dbname=oea user=postgres password=xxx")

        with conn as connection:
        # with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                cursor.execute("DROP TABLE IF EXISTS students")

                # programs: enrolled, available, locked
                # program id: P* (append number of 5 digits)
                # assessments: 0 for incomplete, 1 for complete #idea: Donna, I changed this because it is more intuitive to award 1 for completion!
                # assessment id: a* (append number of 5 digits)

                create_students_table = """ CREATE TABLE students (student_id INTEGER, student_name TEXT DEFAULT NULL, student_email TEXT DEFAULT NULL);"""
                #! do not add P1 and A1 columns because that should be done by admin.


                cursor.execute(create_students_table)
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                cursor.execute("DROP TABLE IF EXISTS programs")

                create_programs_table = """ CREATE TABLE programs (program_id TEXT, program_name TEXT, description TEXT DEFAULT NULL, initial_availability TEXT DEFAULT 'none');"""

                cursor.execute(create_programs_table)

                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                cursor.execute("DROP TABLE IF EXISTS modules")

                create_modules_table = """ CREATE TABLE modules (module_id TEXT, program_id TEXT, module_name TEXT, content_type TEXT, content_link TEXT, module_index INTEGER);"""

                cursor.execute(create_modules_table)

    except Exception as error:
                print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
                sys.exit(1)

if __name__ == '__main__':
    main()
