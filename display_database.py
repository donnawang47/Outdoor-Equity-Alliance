#!/usr/bin/env python

#-----------------------------------------------------------------------
# display.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import os
import sys
import psycopg2

#-----------------------------------------------------------------------

def display_programs_table():
    try:
        conn = psycopg2.connect("dbname=oea user=rmd password=xxx")

        with conn as connection:

        # with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:
                print('-------------------------------------------')
                print('programs')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM programs;")
                table = cursor.fetchall()
                for row in table:
                    print(row)

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def display_users_table():
    try:
        conn = psycopg2.connect("dbname=oea user=rmd password=xxx")
        with conn as connection:
        # with psycopg2.connect(database_url) as connection:
            with connection.cursor() as cursor:
                print('-------------------------------------------')
                print('users')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM users;")
                table = cursor.fetchall()
                for row in table:
                    print(row)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def main():

    # if len(sys.argv) != 1:
    #     print('Usage: python display.py', file=sys.stderr)
    #     sys.exit(1)

    try:
        conn = psycopg2.connect("dbname=oea user=rmd password=xxx")

        with conn as connection:

        # with psycopg2.connect(database_url) as connection:

            with connection.cursor() as cursor:

                print('-------------------------------------------')
                print('users')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM users;")
                table = cursor.fetchall()
                for row in table:
                    print(row)

                print('-------------------------------------------')
                print('modules')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM modules;")
                table = cursor.fetchall()
                for row in table:
                    print(row)

                print('-------------------------------------------')
                print('programs')
                print('-------------------------------------------')
                cursor.execute("SELECT * FROM programs;")
                table = cursor.fetchall()
                for row in table:
                    print(row)

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
