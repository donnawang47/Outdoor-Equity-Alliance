import psycopg2
import queue
import sys
import os

# _database_url = os.getenv('DATABASE_URL')

# this always works
_database_url = 'postgres://oea_user:KTYMB7UGGi1I8wXjXAFr3vvqNbl5lN4X@dpg-cgp3bg0u9tun42rpj98g-a.oregon-postgres.render.com/oea'

# _database_url = os.getenv('DATABASE_URL')
_connection_pool = queue.Queue()
# conn = psycopg2.connect("dbname=oea user=rmd password=xxx")

def _get_connection():
    try:
        conn = _connection_pool.get(block=False)
    except queue.Empty:
        conn = psycopg2.connect(_database_url)
    return conn

def _put_connection(conn):
    _connection_pool.put(conn)

def insert_module(data):
    connection = _get_connection()
    try:
        # with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            # can prob call max
            cursor.execute('BEGIN;')
            statement = """ INSERT INTO modules (module_id, program_id, module_name, content_type, content_link, module_index) VALUES (%s, %s, %s, %s, %s, %s);  """
            param = [data['module_id'], data['program_id'], data['module_name'], data['content_type'], data['content_link'], data['module_index']]

            cursor.execute(statement, param)
            cursor.execute('COMMIT;')
            # connection.commit()

            # modify users table

            # assuming data is a dictionary
            # check if module is an assessment
            # add new assessment column to users table

            if data['content_type'] == "assessment":
                cursor.execute('BEGIN;')
                statement = "ALTER TABLE users"
                # default of 0 = incomplete
                statement += " ADD COLUMN " + data['module_id']
                statement += " INTEGER DEFAULT 0;"
                cursor.execute(statement)
                cursor.execute('COMMIT;')
            return (True, "module inserted")
            #connection.commit()

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def insert_program(data):
    connection = _get_connection()
    try:
        #with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:

        with connection.cursor() as cursor:
            if (data['program_availability'] != 'all' and
                data['program_availability'] != 'none'):
                raise Exception('Program availability must be: all or none')

            # modify program table
            cursor.execute('BEGIN;')

            statement = """
            INSERT INTO programs (program_id, program_name, description, program_availability) VALUES (%s, %s, %s, %s);
            """
            param = [data['program_id'], data['program_name'], data['description'], data['program_availability']]
            cursor.execute(statement, param)


            # modify students table to include new program column
            # with specified program_id as the name of the column
            pgm_status = 'locked'
            if data['program_availability'] == 'all':
                pgm_status= 'available'
            elif data['program_availability'] == 'enroll':
                    pgm_status = 'enrolled'


            stmt_str = "ALTER TABLE users "
            stmt_str += "ADD " + data['program_id']
            stmt_str += " TEXT DEFAULT %s;"
            cursor.execute(stmt_str, [pgm_status])
            cursor.execute('COMMIT;')

            #connection.commit()

            return(True, "success!")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

# insert information about a student into the users table
# insert information about a student into the users table
def insert_student(data): #data is 4-string-tuple
    connection = _get_connection()
    try:
        #with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            statement = """ INSERT INTO users (user_status, user_name, user_email) VALUES ('student', %s, %s);  """
            param = [data['student_name'], data['student_email']]
            cursor.execute(statement, param)

            connection.commit()

            return(True, "successfully added a new student")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

# insert information about an admin into the users table
def insert_admin(data):
    connection = _get_connection()
    try:
        #with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            statement = """ INSERT INTO users (user_status, user_name, user_email) VALUES ('admin', %s, %s);  """
            param = [data['admin_name'], data['admin_email']]
            cursor.execute(statement, param)

            connection.commit()

            return(True, "successfully added a new admin")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

# returns the highest index
def modules_max():
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            statement = "SELECT count(*) FROM modules"
            cursor.execute(statement)
            data = cursor.fetchall()
            return (True, data[0][0])

    except Exception as error:
            err_msg = "A server error occurred. "
            err_msg += "Please contact the system administrator."
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            return (False, err_msg)
    finally:
            _put_connection(connection)

# use this function to create assessment_id as well
def create_module_id():
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            # \d = represents character
            # '\d+\ = represents any charcter (one or more occurrences)
            # ::INTEGER = cast id to integers before sorting.
            stmt_str = """SELECT substring(module_id FROM '\d+')
            from modules ORDER BY substring(module_id FROM '\d+')::INTEGER
            DESC limit 1 """
            cursor.execute(stmt_str)
            data = cursor.fetchall()
            # print("create module_id: ", count)
            num = 1
            if len(data) != 0:
                print('data = ', data)
                id = data[0][0]
                print('id = ', id)
                num = int(id) + 1
                print('num = ', num)
            module_id = 'm' + str(num)
            print("create module id:", module_id)
            connection.commit()
            return (True, module_id)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def create_program_id():
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                # stmt_str = "SELECT COUNT(*) FROM programs"
                stmt_str = """SELECT substring(program_id FROM '\d+')
            from programs ORDER BY substring(program_id FROM '\d+')::INTEGER
            DESC LIMIT 1"""
                cursor.execute(stmt_str)
                data = cursor.fetchall()
                num = 1
                if len(data) != 0:
                    print('count =', data[0][0])
                    # print("program id", count[0][0])
                    id = data[0][0]
                    num = int(id) + 1
                print('num = ', num)
                program_id = 'p' + str(num)
                # print("create program id:", program_id)
                print('program id created = ', program_id)
                connection.commit()
                return (True, program_id)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def get_user_id(student_email):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            stmt_str = "SELECT user_id FROM users WHERE user_email= %s"
            cursor.execute(stmt_str, [student_email])
            data = cursor.fetchall()
            # print("program id", count[0][0])
            student_id = data[0][0]
            # print("create program id:", program_id)

            return student_id

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def get_program_id(program_name):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            statement = "SELECT program_id FROM programs WHERE"
            statement += " program_name = %s"
            cursor.execute(statement, [program_name])
            data = cursor.fetchall()
            # print("program id", count[0][0])
            program_name = data[0][0]
            # print("create program id:", program_id)
            return (True, program_name)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

#! might have to delete later (not needed?)
def get_module_id(module_name):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            statement = "SELECT module_id FROM modules WHERE"
            statement += " module_name = %s"
            cursor.execute(statement, [module_name])
            data = cursor.fetchall()
            # print("program id", count[0][0])
            program_name = data[0][0]
            # print("create program id:", program_id)
            return (True, program_name)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)



#! to do: update programs and asessments status for student
    # assessment = updated once the student completes quiz
    # program = updated once the student completes program or with admin permission
def update_assessment_status(student_id, assessment_id, status):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute('BEGIN')

            stmt_str = "UPDATE users SET "
            stmt_str += assessment_id
            stmt_str += "=%s WHERE user_id=%s;"

            cursor.execute(stmt_str, [status, student_id])

            cursor.execute('COMMIT')
            print("Transaction committed")
            return (True, "assessment status changed")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)


# status: locked, available, enrolled
def update_program_status(student_id, program_id, status):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute('BEGIN')

            #
            stmt_str = "UPDATE users SET "
            stmt_str += program_id
            stmt_str += "= %s WHERE user_id = %s"

            cursor.execute(stmt_str, [status, student_id])
            cursor.execute('COMMIT')
            print("Transaction committed")
            return (True, "program status changed")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def delete_program(program_id):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                # remove program from students table
                cursor.execute('BEGIN;')
                statement = " ALTER TABLE users DROP COLUMN "
                statement += program_id
                cursor.execute(statement)
                cursor.execute('COMMIT;')
                #connection.commit()

                # remove program from programs table
                statement = "DELETE FROM programs WHERE program_id = %s"
                cursor.execute(statement, [program_id])
                #connection.commit()

                # remove program from modules table
                statement = "DELETE FROM modules WHERE program_id = %s"
                cursor.execute(statement, [program_id])

                #connection.commit()
                return (True, "deleted program successfully")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)


def delete_module(module_id):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            print("modify_database.py: delete_module", module_id)
            # fetch content type with module_id
            statement = "SELECT content_type FROM modules WHERE "
            statement += "module_id = %s"
            #statement += str(module_id)
            cursor.execute(statement, [module_id])
            content_type = cursor.fetchall()

            print("getting content type...")
            print("content_type = ", content_type)

            # determine if module id corresponds to assessment.
            # if so, delete its assessment column from students table.
            if content_type[0][0] == 'assessment':
                print('content-type =', content_type[0][0])
                print("is assessment")

                cursor.execute('BEGIN;')
                statement = "ALTER TABLE users DROP COLUMN "
                statement += str(module_id)
                cursor.execute(statement)
                cursor.execute('COMMIT;')

            # delete row with specified module id from programs table
            statement = "DELETE FROM modules WHERE module_id = %s"
            # statement += str(module_id)
            cursor.execute(statement, [module_id])
            return(True, "module successfully deleted")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)


def change_program_name(program_id, new_program_name):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            cursor.execute('BEGIN')
            statement = "UPDATE programs SET program_name= "
            statement += "%s WHERE program_id = %s"

            cursor.execute(statement, [new_program_name, program_id])

            cursor.execute('COMMIT')
            print('Program name successfully updated!')
            return (True, "success!")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)

def change_program_desc(pgm_id, new_program_desc):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            cursor.execute('BEGIN')
            statement = "UPDATE programs SET description= "
            statement += "%s WHERE program_id = %s"

            cursor.execute(statement, [new_program_desc, pgm_id])

            cursor.execute('COMMIT')
            print('Program desc successfully updated!')
            return (True, "success!")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)

def change_program_avail(pgm_id, new_program_avail):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            cursor.execute('BEGIN')
            statement = "UPDATE programs SET program_availability= "
            statement += "%s WHERE program_id = %s"

            cursor.execute(statement, [new_program_avail, pgm_id])

            cursor.execute('COMMIT')
            print('Program avail successfully updated!')
            return (True, "success!")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)

def change_module_name(module_id, new_module_name):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            print('module_id for changing name: ', module_id)
            print('new name for module: ', new_module_name)
            cursor.execute('BEGIN')
            statement = "UPDATE modules SET module_name="
            statement += "%s WHERE module_id= %s"

            cursor.execute(statement, [new_module_name, module_id])

            cursor.execute('COMMIT')
            print('Module name successfully updated!')
            return (True, "success!")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)

def edit_module_link(new_module_link, id):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute('BEGIN')
            statement = "UPDATE modules SET content_link= %s"
            statement += " WHERE module_id= %s"

            cursor.execute(statement, [new_module_link, id])

            cursor.execute('COMMIT')
            print('Progran name successfully updated!')
            return (True, "success!")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)


def change_module_idx(module_id, new_idx):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            print('modify_database: change_module_idx')
            cursor.execute('BEGIN')
            statement = "UPDATE modules SET module_index= %s"
            statement += " WHERE module_id= %s"

            cursor.execute(statement, [new_idx, module_id])

            cursor.execute('COMMIT')
            print('Success modify_database: change_module_idx')
            return (True, "success!")

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)

# compares passed program name to all program names in database to
# check if there are duplicates
def isProgramNameDuplicate(newName):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            statement = "SELECT program_name FROM programs"
            cursor.execute(statement)

            names = cursor.fetchall()

            for name in names:
                if newName == name:
                    return True

            return False

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)

# compares passed program name to all program names in database to
# check if there are duplicates
def isModuleNameDuplicate(newName):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            statement = "SELECT module_name FROM modules"
            cursor.execute(statement)

            names = cursor.fetchall()

            for name in names:
                if newName == name:
                    return True

            return False

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)


# write functionality to deal with duplicate entries!
def main():
#    valid, num = modules_max()
#    print('max index = ', num)

    # ----------------------------------------------------------------
    # delete_module('m10')
    # delete_program('p5')
    # change_module_idx('m3', 1)
    # change_module_idx('m2', 2)
    #change_program_desc('p1', 'new p1 desc')
    # change_program_avail('p1', 'none')
    # #  ! must pass in data to be inserted into modules table from interface interaction.

    # #----------------- testing creating program id --------------------
    # id = create_program_id()
    # print('Newly created program id = ', id)

    # # ? what are the different types of contents?

    # # create new program: Tree Ambassador 101
    # print("program id: create program id")
    program1_id = create_program_id()
    print("program1 id:", program1_id)
    # program1_data = {"program_id": program1_id,
    #                 "program_name": "Tree Ambassador 101",
    #                 "description": "Description",
    #                 "program_availability": "all"
    #                 }
    # print('data: ', program1_data)
    # # program1_data = [program1_id, "Tree Ambassador 101", "Description", "all"]
    # insert_program(program1_data)
    # print("main: insert program1")

    # # # insert module 1 of tree ambassador 101
    module1_id = create_module_id()
    print("module1 id: ", module1_id)
    # module1_name = 'M1 Instructions'
    # module1_content_type = "text"
    # module1_content_link = 'https://docs.google.com/document/d/1PP-GiTqVcvJYpqVUxQ_bXSsru6H200l39RovL0AhYgw/edit?usp=sharing'
    # module1_index = 0 #idea: need a function to get index
    # #! will get index from input text form from the admin; another function
    # #! should switch orders of indexes.
    # module1_data = {
    #     'module_id' : module1_id,
    #     'program_id': program1_id,
    #     'module_name': module1_name,
    #     'content_type': module1_content_type,
    #     'content_link': module1_content_link,
    #     'module_index': module1_index
    # }


    # insert_module(module1_data)
    # print("main: insert module1")


    # # insert module 2 of tree ambassador 101
    # module2_id = create_module_id()
    # print('module2 id: ', module2_id)
    # module2_name = 'Module 1 Learning Exercise' # module 1 not a typo
    # module2_content_type = "assessment"
    # module2_content_link = 'https://docs.google.com/forms/d/e/1FAIpQLScGFPXzgFiIaIc5R7NQW_OvINY7y7xc4UHHhIIkt-4AJ-TZoQ/viewform'
    # module2_index = 1 # need a function to get index


    # module2_data = {
    #     'module_id' : module2_id,
    #     'program_id': program1_id,
    #     'module_name': module2_name,
    #     'content_type': module2_content_type,
    #     'content_link': module2_content_link,
    #     'module_index': module2_index
    # }


    # insert_module(module2_data)
    # print("main: insert module2")

    # # adding second assessment module
    # module4_id = create_module_id()
    # print('module4 id: ', module4_id)
    # module4_name = 'p1 assessment2' # module 1 not a typo
    # module4_content_type = "assessment"
    # module4_content_link = 'module4 link'
    # module4_index = 2 # need a function to get index

    # # module2_data = [module2_id, program1_id, module2_name, module2_content_type, module2_content_link, module2_index]

    # module4_data = {
    #     'module_id' : module4_id,
    #     'program_id': program1_id,
    #     'module_name': module4_name,
    #     'content_type': module4_content_type,
    #     'content_link': module4_content_link,
    #     'module_index': module4_index
    # }


    # insert_module(module4_data)
    # print("main: insert module4")

    # # # # # ------------creating test programs -------------------- #

    # # # # create locked program
    # program2_id = create_program_id()
    # program2_data = {
    #     "program_id": program2_id,
    #     "program_name": "Course 105",
    #     "description": "Description",
    #     "program_availability": "none"
    # }
    # insert_program(program2_data)
    # print("main: program2 inserted")

    # # # create random module in program2
    # module3_id = create_module_id()
    # module3_name = 'test module' # module 1 not a typo
    # module3_content_type = "content type"
    # module3_content_link = 'content link'
    # module3_index = 0 # need a function to get index


    # module3_data = {
    #     'module_id' : module3_id,
    #     'program_id': program2_id,
    #     'module_name': module3_name,
    #     'content_type': module3_content_type,
    #     'content_link': module3_content_link,
    #     'module_index': module3_index
    # }


    # insert_module(module3_data)
    # print("main: insert module3")


    # # # # #--------------test adding students -------------------------- #

    # # add Liz as student
    # print('add student1 Liz')
    # student_data = {
    #      'student_name': 'Liz Garcia',
    #      'student_email': 'lg6248@princeton.edu'
    # }
    # insert_student(student_data)

    # # add Annie as student
    # print('add student2 Annie')
    # student_data = {
    #      'student_name': 'Annie Liu',
    #      'student_email': 'an2334@princeton.edu'
    # }
    # insert_student(student_data)

    # # add Donna as student
    # print('add student3 Donna')
    # student_data = {
    #      'student_name': 'Donna Wang',
    #      'student_email': 'dw5609@princeton.edu'
    # }
    # insert_student(student_data)

    #display_database.display_programs_table()

    # # ----------- test changing program name ------------------------#
    # print('changing course 105 to course #2')

    # change_program_name('P2', 'Course #2')
    # print('Changed program name successfully!')

    # # ----------- test update_assessment_status -------------------#
    # update status for Liz to 1 (complete)
    # Liz_id = get_user_id('lg6248@princeton.edu')
    # print(Liz_id)
    # print(program1_id)
    # # update_assessment_status(Liz_id, module2_id, 1)

    # # # change status back to incomplete for Liz
    # # update_assessment_status(Liz_id, module2_id, 0)

    # # # update status for Annie
    # Annie_id = get_user_id('an2334@princeton.edu')
    # # # update_assessment_status(Annie_id, module2_id, 1)

    # # # # update status for Donna
    # Donna_id = get_user_id('dw5609@princeton.edu')
    # # update_assessment_status(Donna_id, module2_id, 1)

    # # ----------- test update_program_status ----------------------#

    # # update status for Liz to 1 (complete)
    # update_program_status(Liz_id, program1_id, 'locked')

    # # change status back to incomplete for Liz
    # update_program_status(Liz_id, program1_id, 'enrolled')

    # # update status for Annie
    # update_program_status(Annie_id, program1_id, 'locked')

    # # update status for Donna
    # update_program_status(Donna_id, program1_id, 'locked')

    # #------------- test delete_program-----------------------------#

    # # delete program 1
    # delete_program(program1_id)

    # delete program 2
    # delete_program(program2_id)

    # #----------------- delete_module------------------------------#

    # # delete module 1 of program 1
    # delete_module(module1_id)


    # # delete module 2 of program 1 (assessment)
    # delete_module(module2_id)



if __name__ == '__main__':
    main()
