import psycopg2
import sys
import os

DATABASE_URL = os.getenv('DATABASE_URL')

def insert_module(data, quiz_num):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                # need to get module id

                statement = """ INSERT INTO modules (module_id, program_id, module_name, content_type, content_link, module_index) VALUES (%s, %s, %s, %s, %s, %s)  """
                cursor.execute(statement, data)

                result = data.count('quiz')

                # update students table: if a quiz is being added in a program, add new quiz column into students table.
                #! even if we add extra columns for every additional program in the students table, how will we know a quiz is for program1 or program2? I think we need seperate tables
                if result > 0:
                     cursor.execute(""" ALTER TABLE students""" )
                     program_Num += 1
                     statement = " ADD COLUMN quiz" + str(quiz_num) + " INTEGER DEFAULT 0"
                     cursor.execute(statement)


    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

def insert_program(data):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:

            with connection.cursor() as cursor:

                # need to get program_id

                statement = """
                INSERT INTO programs (program_id, program_name, description, initial_availability) VALUES (%s, %s, %s, %s)
                """
                cursor.execute(statement, data)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        sys.exit(1)

def insert_students(data):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                # need to get student id

                statement = """ INSERT INTO students (student_id, student_name, student_email) VALUES (%s, %s, %s, %s)  """
                cursor.execute(statement, data)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)




def add_new_program():



def main():
     #! must pass in data to be inserted into modules table from interface interaction.
     data = [1, 'Module 1', 'lesson 1.1', 'google doc', 'https://docs.google.com/document/d/1QObJ5USYw30AdCjBgP9LFBSu8MTCZZqiB8jriQlzhF8/edit?usp=sharing', 1]

     insert_module(data)


if __name__ == '__main__':
    main()
