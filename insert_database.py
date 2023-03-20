import psycopg2
import sys
import os

DATABASE_URL = os.getenv('DATABASE_URL')

def insert_module(data, quiz_num):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                # need to get module id

                statement = """ INSERT INTO modules (module_id, program_id, module_name, content_type, content_link, module_index) VALUES (%s, %s, %s, %s, %s, %s);  """
                cursor.execute(statement, data)

                result = data.count('quiz')

                # update students table: if a quiz is being added in a program, add new quiz column into students table.
                #! even if we add extra columns for every additional program in the students table, how will we know a quiz is for program1 or program2? I think we need seperate tables
                if result > 0:
                     cursor.execute(""" ALTER TABLE students;""" )
                     program_Num += 1
                     statement = " ADD COLUMN quiz" + str(quiz_num) + " INTEGER DEFAULT 0;"
                     cursor.execute(statement)


    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

# use this function to create assessment_id as well
def create_module_id():
    module_id = 'M'
    stmt_str = "SELECT COUNT(*) FROM modules"
    cursor.execute(stmt_str)
    module_id+= cursor.fetchall()
    return module_id

def create_program_id():
    program_id = 'P'
    stmt_str = "SELECT COUNT(*) FROM programs"
    cursor.execute(stmt_str)
    program_id+= cursor.fetchall()
    return program_id

def insert_module(data):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                # modify modules table

                # needs a function to get module_index
                # can prob call max
                statement = """ INSERT INTO modules (module_id, program_id, module_name, content_type, content_link, module_index) VALUES (%s, %s, %s, %s, %s, %s);  """
                cursor.execute(statement, data)

                # modify students table

                # assuming data is a dictionary
                # check if module is an assessment
                # add new assessment column to students table
                if data['content_type'] == "assessment":
                    insert_assessment_col(data['module_id'])

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)


# helper method to insert new assessment into student table
def insert_assessment_col(assessment_id):
    cursor.execute("ALTER TABLE students;")
    stmt_str = "ADD" + str(assessment_id) + #! ADD COLUMN [name]
                " INTEGER DEFAULT 0;"
    cursor.execute(stmt_str)

# helper method to insert new program into student table
def insert_program_col(program_id):
    cursor.execute("ALTER TABLE students;")
    stmt_str = "ADD" + str(assessment_id) +
                " TEXT DEFAULT 'locked';"
    cursor.execute(stmt_str)


def insert_program(data):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:

            with connection.cursor() as cursor:

                # modify program table

                statement = """
                INSERT INTO programs (program_id, program_name, description, initial_availability) VALUES (%s, %s, %s, %s);
                """
                cursor.execute(statement, data)

                # modify student table
                insert_program_col(data['program_id'])

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        sys.exit(1)

def insert_students(data):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                statement = """ INSERT INTO students (student_id, student_name, student_email) VALUES (%s, %s, %s, %s);  """
                cursor.execute(statement, data)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)



def main():
     #! must pass in data to be inserted into modules table from interface interaction.

    # what are the different types of contents?

    # create new program: Tree Ambassador 101
    program_id = create_program_id()
    program_data = [program_id, "Tree Ambassador 101", "Description", "ALL"]
    insert_program(program_data)


    # insert module 1 of tree ambassador 101
    module1_id = create_module_id()
    module1_name = 'START HERE Module 1 Instructions'
    module1_content_type = "text"
    module1_content_link = 'https://docs.google.com/document/d/1PP-GiTqVcvJYpqVUxQ_bXSsru6H200l39RovL0AhYgw/edit?usp=sharing'
    module1_index = 1 # need a function to get index

    module1_data = [module1_id, program_id, module1_name, module1_content_type, module1_content_link, module1_index]

    insert_module(module1_data)


    # insert module 2 of tree ambassador 101
    # i think this is an assessment, but it's not google form
    module2_id = create_module_id()
    module2_name = 'Module 1 Learning Exercise'
    module2_content_type = "assessment"
    module2_content_link = 'https://docs.google.com/presentation/d/10CqURw5FXmLZMroucKVMdKSbmIe7-tyr/edit?usp=sharing&ouid=115342626022865620149&rtpof=true&sd=true'
    module2_index = 2 # need a function to get index

    module2_data = [module2_id, program_id, module2_name, module2_content_type, module2_content_link, module2_index]

    insert_module(module2_data)


    # ----------- creating test programs ---------------

    # create locked program
    program_id = create_program_id()
    program_data = [program_id, "LOCKED PROGRAM", "Description", "NONE"]
    insert_program(program_data)


if __name__ == '__main__':
    main()
