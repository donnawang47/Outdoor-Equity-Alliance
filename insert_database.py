import psycopg2
import sys
import os

DATABASE_URL = os.getenv('DATABASE_URL')

def insert_module(data):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                # need to get module id

                insert_link_statement = """ INSERT INTO modules (module_id, program_name, module_name, content_type, content_link, module_index) VALUES (%s, %s, %s, %s, %s, %s)  """
                cursor.execute(insert_link_statement, data)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

def insert_program(data):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:

            with connection.cursor() as cursor:

                # need to get program_id

                stmt_str = """
                INSERT INTO programs (program_id, program_name, description, initial_availability) VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_link_statement, data)

    except Exception as ex:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        sys.exit(1)

def insert_students(data):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                # need to get student id

                insert_link_statement = """ INSERT INTO students (student_id, student_name, student_email) VALUES (%s, %s, %s, %s)  """
                cursor.execute(insert_link_statement, data)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

def add_program():




def main():
     #! must pass in data to be inserted into modules table.
     data = [1, 'Module 1', 'lesson 1.1', 'google doc', 'https://docs.google.com/document/d/1QObJ5USYw30AdCjBgP9LFBSu8MTCZZqiB8jriQlzhF8/edit?usp=sharing', 1]

     insert_module(data)


if __name__ == '__main__':
    main()
