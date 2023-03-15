import sqlite3
import contextlib
import sys

DATABASE_URL = 'file:reg.sqlite?mode=rwc'

def insert(data):
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level = None,
        uri = True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:

                insert_link_statement = """ INSERT INTO modules (module_id INTEGER, program_name INTEGER,
                    module_name TEXT, content_type TEXT, content_link
                    BLOB, module_index INTEGER) VALUES (?, ?, ?, ?, ?, ?)  """
                cursor.execute(insert_link_statement, data)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

def main():
     #! must pass in data to be inserted in modules table.
     data = [1, 'Module 1', 'lesson 1.1', 'google doc', 'https://docs.google.com/document/d/1QObJ5USYw30AdCjBgP9LFBSu8MTCZZqiB8jriQlzhF8/edit?usp=sharing', 1]
     
     insert(data)


if __name__ == '__main__':
    main()
