import psycopg2
import sys
import os

DATABASE_URL = os.getenv('DATABASE_URL')
CONN = psycopg2.connect("dbname=oea user=postgres password=xxx")


#TODO: get module_id, program_id, student_id efficeintly. Use max()
#TODO: postgress function?

def add_assessment_column(module_id):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                cursor.execute(""" ALTER TABLE students""" )
                # default of 0 = incomplete
                statement = " ADD COLUMN A" + str(module_id) + \
                            " INTEGER DEFAULT 0;"
                cursor.execute(statement)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)


def insert_module(data):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                # can prob call max
                statement = """ INSERT INTO modules (module_id, program_id, module_name, content_type, content_link, module_index) VALUES (%s, %s, %s, %s, %s, %s);  """
                param = [data['module_id'], data['program_id'], data['module_name'], data['content_type'], data['content_link'], data['module_index']]

                cursor.execute(statement, param)

                # modify students table

                # assuming data is a dictionary
                # check if module is an assessment
                # add new assessment column to students table
                if data['content_type'] == "assessment":
                    statement = "ALTER TABLE students"
                    # default of 0 = incomplete
                    statement += " ADD " + data['module_id']
                    statement += " INTEGER DEFAULT 0;"
                    cursor.execute(statement)

                    # add_assessment_column(str(data['module_id']))

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

def insert_program(data):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:

            with connection.cursor() as cursor:
                if(data['program_availability'] != 'all' and
                    data['program_availability'] != 'none'):
                    raise Exception('Input must be: all or none')

                # modify program table
                statement = """
                INSERT INTO programs (program_id, program_name, description, program_availability) VALUES (%s, %s, %s, %s);
                """
                param = [data['program_id'], data['program_name'], data['description'], data['program_availability']]
                cursor.execute(statement, param)

                # modify students table to include new program column
                # with specified program_id as the name of the column
                stmt_str = "ALTER TABLE students "
                stmt_str += "ADD " + data['program_id']
                stmt_str += " TEXT DEFAULT 'locked';"
                cursor.execute(stmt_str)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        sys.exit(1)

# insert information about a student into the students table
def insert_student(data):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                statement = """ INSERT INTO students (student_id, student_name, student_email) VALUES (%s, %s, %s, %s);  """
                cursor.execute(statement, data)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

# returns student_id based on existing numebr of columns in students table
def create_student_id():
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                statement = "SELECT COUNT(*) FROM students"
                cursor.execute(statement)
                data = cursor.fetchall()
                id = 1 + data[0]
                print("create student id:", id)

                return id

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)


# use this function to create assessment_id as well
def create_module_id():
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                module_id = 'M'
                stmt_str = "SELECT COUNT(*) FROM modules"
                cursor.execute(stmt_str)
                count = cursor.fetchall()
                # print("create module_id: ", count)

                module_id+= str(count[0][0] + 1)
                print("create module id:", module_id)
                return module_id

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

def create_program_id():
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:

                program_id = 'P'
                stmt_str = "SELECT COUNT(*) FROM programs"
                cursor.execute(stmt_str)
                count = cursor.fetchall()
                # print("program id", count[0][0])
                program_id+= str(count[0][0] + 1)
                # print("create program id:", program_id)
                return program_id

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

#! to do: update programs and asessments status for student
    # assessment = updated once the student completes quiz
    # program = updated once the student completes program or with admin permission
def update_assessment_status(student_id, assessment_id, status ):
     try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute('BEGIN')

                statement = " UPDATE students SET "
                statement += str(assessment_id)
                statement += " = "
                statement += str(status)
                statement += " WHERE student_id = "
                statement += str(student_id)

                cursor.execute(statement, [student_id, assessment_id, status])

                cursor.execute('COMMIT')
                print("Transaction committed")

     except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

def update_program_status(student_id, program_id, status):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute('BEGIN')

                statement = " UPDATE students SET "
                statement += str(program_id)
                statement += " = "
                statement += str(status)
                statement += " WHERE student_id = "
                statement += str(student_id)

                cursor.execute(statement, [student_id, program_id, status])

                cursor.execute('COMMIT')
                print("Transaction committed")

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

def delete_program(program_id):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                 # remove program from students table
                 statement = " ALTER TABLE students DROP COLUMN "
                 statement += str(program_id)
                 cursor.execute(statement)

                 # remove program from programs table
                 statement = "DELETE FROM programs WHERE program_id = "
                 statement += str(program_id)
                 cursor.execute(statement)


                 # remove program from modules table
                 statement = "DELETE FROM modules WHERE program_id =  "
                 statement += str(program_id)
                 cursor.execute(statement)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)


def delete_module(module_id):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                # fetch content type with module_id
                statement = "SELECT content_type FROM modules WHERE "
                statement += "module_id = "
                statement += str(module_id)
                cursor.execute(statement)
                content_type = cursor.fetchall()

            # determine if module id corresponds to assessment.
            # if so, delete its assessment column from students table.
                if content_type[0] == 'assessment':
                     statement = "ALTER TABLE students DROP COLUMN "
                     statement += str(module_id)
                     cursor.execute(statement)

            # delete row with specified module id from programs table
                statement = "DELETE FROM programs WHERE module_id = "
                statement += str(module_id)
                cursor.execute(statement)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        sys.exit(1)


def main():
     #! must pass in data to be inserted into modules table from interface interaction.

    #? what are the different types of contents?

    # create new program: Tree Ambassador 101
    print("main: create program id")
    program1_id = create_program_id()
    print("main:", program1_id)
    program1_data = {"program_id": program1_id,
                    "program_name": "Tree Ambassador 101",
                    "description": "Description",
                    "program_availability": "all"
                    }
    # program1_data = [program1_id, "Tree Ambassador 101", "Description", "all"]
    insert_program(program1_data)
    print("main: insert program1")

    # insert module 1 of tree ambassador 101
    module1_id = create_module_id()
    print("main: ", module1_id)
    module1_name = 'START HERE Module 1 Instructions'
    module1_content_type = "text"
    module1_content_link = 'https://docs.google.com/document/d/1PP-GiTqVcvJYpqVUxQ_bXSsru6H200l39RovL0AhYgw/edit?usp=sharing'
    module1_index = 1 # need a function to get index
    #! will get index from input text form from the admin; another function
    #! should switch orders of indexes.
    module1_data = {
        'module_id' : module1_id,
        'program_id': program1_id,
        'module_name': module1_name,
        'content_type': module1_content_type,
        'content_link': module1_content_link,
        'module_index': module1_index
    }

    # module1_data = [module1_id, program_id, module1_name, module1_content_type, module1_content_link, module1_index]

    insert_module(module1_data)
    print("main: insert module1")


    # insert module 2 of tree ambassador 101
    module2_id = create_module_id()
    module2_name = 'Module 1 Learning Exercise' # module 1 not a typo
    module2_content_type = "assessment"
    module2_content_link = 'https://docs.google.com/forms/d/e/1FAIpQLScGFPXzgFiIaIc5R7NQW_OvINY7y7xc4UHHhIIkt-4AJ-TZoQ/viewform'
    module2_index = 2 # need a function to get index

    # module2_data = [module2_id, program1_id, module2_name, module2_content_type, module2_content_link, module2_index]

    module2_data = {
        'module_id' : module2_id,
        'program_id': program1_id,
        'module_name': module2_name,
        'content_type': module2_content_type,
        'content_link': module2_content_link,
        'module_index': module2_index
    }


    insert_module(module2_data)
    print("main: insert module2")

    # ------------creating test programs -------------------- #

    # create locked program
    program2_id = create_program_id()
    program2_data = {
        "program_id": program2_id,
        "program_name": "LOCKED PROGRAM",
        "description": "Description",
        "program_availability": "none"
    }
    # program2_data = [program2_id, "LOCKED PROGRAM", "Description", "NONE"]
    insert_program(program2_data)
    print("main: program2 inserted")

    #--------------test adding students -------------------------- #

    # add student1 Liz
    student1_id = create_student_id()
    student_data = [student1_id, 'Liz Garcia', 'lg6248@princeton.edu']
    insert_student(student_data)

    # add student2 Annie
    student2_id = create_student_id()
    student_data = [student2_id, 'Annie Liu', 'an2334@princeton.edu']
    insert_student(student_data)

    # add student3 Donna
    student3_id = create_student_id()
    student_data = [student3_id, 'Donna Wang', 'dw5609@princeton.edu']
    insert_student(student_data)

    #Idea: when we add a student, what happens with the value in programs and assessments columns?

    # ----------- test update_assessment_status -------------------#
    # update status for Liz to 1 (complete)
    update_assessment_status(student1_id, module2_id, 1)

    # change status back to incomplete for Liz
    update_assessment_status(student1_id, module2_id, 0)

    # update status for Annie
    update_assessment_status(student2_id, module2_id, 1)

    # update status for Donna
    update_assessment_status(student3_id, module2_id, 1)

    # ----------- test update_program_status ----------------------#

    # update status for Liz to 1 (complete)
    update_program_status(student1_id, program_id, 'locked')

    # change status back to incomplete for Liz
    update_program_status(student1_id, program_id, 'enrolled')

    # update status for Annie
    update_program_status(student2_id, program_id, 'locked')

    # update status for Donna
    update_program_status(student3_id, program_id, 'locked')

    #------------- test delete_program-----------------------------#

    # delete program 1
    delete_program(program1_id)

    #----------------- delete_module------------------------------#

    # delete module 1 of program 1
    delete_module(module1_id)


    # delete module 2 of program 1 (assessment)
    delete_module(module2_id)



if __name__ == '__main__':
    main()
