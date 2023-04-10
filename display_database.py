#!/usr/bin/env python

#-----------------------------------------------------------------------
# display.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import psycopg2
import sys
import os
import queue

#-----------------------------------------------------------------------

_database_url = os.getenv('DATABASE_URL')
_connection_pool = queue.Queue()

def _get_connection():
    try:
        conn = _connection_pool.get(block=False)
    except:
        conn = psycopg2.connect(_database_url)
    return conn

def _put_connection(conn):
    _connection_pool.put(conn)

#-------------------------------------------------------

def display_programs_table():
    connection = _get_connection()
    try:
        # conn = psycopg2.connect("dbname=oea user=rmd password=xxx")

        # with conn as connection:

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
    finally:
        _put_connection(connection)

def display_users_table():
    connection = _get_connection()
    try:
        # conn = psycopg2.connect("dbname=oea user=rmd password=xxx")
        # with conn as connection:
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
    finally:
        _put_connection(connection)

def main():

    # if len(sys.argv) != 1:
    #     print('Usage: python display.py', file=sys.stderr)
    #     sys.exit(1)

    connection = _get_connection()
    try:
        # conn = psycopg2.connect("dbname=oea user=rmd password=xxx")
        # with conn as connection:

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
    finally:
        _put_connection(connection)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
