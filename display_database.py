#!/usr/bin/env python

#-----------------------------------------------------------------------
# display.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import os
import sys
import psycopg2

#-----------------------------------------------------------------------

def main():

    if len(sys.argv) != 1:
        print('Usage: python display.py', file=sys.stderr)
        sys.exit(1)

    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect("dbname=oea user=postgres password=xxx")

        with conn as connection:

        # with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                print('-------------------------------------------')
                print('students')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM students")
                table = cursor.fetchall()
                for row in table:
                    print(row)

                print('-------------------------------------------')
                print('modules')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM modules")
                table = cursor.fetchall()
                for row in table:
                    print(row)

                print('-------------------------------------------')
                print('programs')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM programs")
                table = cursor.fetchall()
                for row in table:
                    print(row)

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
