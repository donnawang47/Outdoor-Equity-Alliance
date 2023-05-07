import psycopg2
import queue
import sys
import os

_database_url = os.getenv('DATABASE_URL')

_connection_pool = queue.Queue()
# conn = psycopg2.connect("dbname=oea user=rmd password=xxx")
# $env:DATABASE_URL="postgres://oea_user:KTYMB7UGGi1I8wXjXAFr3vvqNbl5lN4X@dpg-cgp3bg0u9tun42rpj98g-a.oregon-postgres.render.com/oea"

def _get_connection():
    try:
        conn = _connection_pool.get(block=False)
    except queue.Empty:
        conn = psycopg2.connect(_database_url)
    return conn

def _put_connection(conn):
    _connection_pool.put(conn)


def insert_student(data):
    #data is a dict which contains two key-values pairs, with keys student_name and student_email
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #check for missing arguments
            for key, value in data.items():
                if value is None or value == '':
                    raise Exception("missing " + str(key))

            cursor.execute('BEGIN')

            #check for duplicates via user_email
            statement = "SELECT FROM users WHERE user_email = %s;"
            cursor.execute(statement, [data['student_email']])
            table = cursor.fetchall()
            if len(table) != 0:
                raise Exception("email already in database")

            #create user_id
            statement = "SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1;"
            cursor.execute(statement)
            table = cursor.fetchall()

            if len(table) != 0:
                user_id = int(table[0][0]) + 1
            else:
                user_id = 1

            #insert student info into users table
            statement = "INSERT INTO users (user_id, user_name, user_email, user_status) VALUES (%s, %s, %s, 'student');"
            params = [user_id, data['student_name'], data['student_email']]
            cursor.execute(statement, params)

            #update program_status table
            statement = "SELECT program_id, program_availability FROM programs;"
            cursor.execute(statement)
            table = cursor.fetchall()

            for row in table:
                #row[0] is program_id
                #row[1] is the program_availability
                if row[1] == 'all':
                    user_program_status = 'available'
                else:
                    user_program_status = 'locked'

                statement = "INSERT INTO program_status (user_id, program_id, user_program_status) VALUES (%s, %s, %s);"
                params = [user_id, row[0], user_program_status]
                cursor.execute(statement, params)


            #update assessment_status table
            statement = "SELECT module_id FROM modules WHERE modules.content_type = 'assessment';"
            cursor.execute(statement)
            table = cursor.fetchall()

            for row in table:
                statement = "INSERT INTO assessment_status (user_id, module_id, user_assessment_status) VALUES (%s, %s, %s);"
                # default 0 for incomplete
                params = [user_id, row[0], 0]
                cursor.execute(statement, params)

            cursor.execute('COMMIT')

            return (True, "successfully added a new student")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)



def insert_admin(data):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #check for missing arguments
            for key, value in data.items():
                if value is None or value == '':
                    raise Exception("missing " + str(key))

            cursor.execute('BEGIN')

            #check for duplicates via user_email
            statement = "SELECT FROM users WHERE user_email = %s;"
            cursor.execute(statement, [data['admin_email']])
            table = cursor.fetchall()
            if len(table) != 0:
                raise Exception("email already in database")

            #generate user_id
            statement = "SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1;"
            cursor.execute(statement)
            table = cursor.fetchall()

            if len(table) != 0:
                user_id = int(table[0][0]) + 1
            else:
                user_id = 1

            # insert admin info into users table
            statement = "INSERT INTO users (user_id, user_name, user_email, user_status) VALUES (%s, %s, %s, 'admin');"
            params = [user_id, data['admin_name'], data['admin_email']]
            cursor.execute(statement, params)

            cursor.execute('COMMIT')

            return (True, "successfully added a new admin")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def delete_user(user_id):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('BEGIN')

            statement = "DELETE FROM users WHERE user_id=%s;"
            cursor.execute(statement, [user_id])

            statement = "DELETE FROM program_status WHERE user_id=%s;"
            cursor.execute(statement, [user_id])

            statement = "DELETE FROM assessment_status WHERE user_id=%s;"
            cursor.execute(statement, [user_id])

            cursor.execute('COMMIT')

            return(True, "successfully deleted user")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def insert_program(data):
    #data is a dict containing 3 values: name , desc, avail

    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            #check for missing arguments
            for key, value in data.items():
                if value is None or value == '':
                    raise Exception("missing " + str(key))

            cursor.execute('BEGIN')

            if data['program_availability'] != 'all' and data['program_availability'] != 'none':
                raise Exception('program availability must be all or none')

            #! check for duplicates via program name
            statement = "SELECT FROM programs WHERE program_name = %s;"
            cursor.execute(statement, [data['program_name']])
            table = cursor.fetchall()
            if len(table) != 0:
                raise Exception("program name conflict, insertion aborted")

            # generate program_id
            statement = """SELECT substring(program_id FROM '\d+')
                from programs ORDER BY substring(program_id FROM '\d+')::INTEGER
                DESC LIMIT 1;"""
            cursor.execute(statement)
            table = cursor.fetchall()

            if len(table) != 0:
                num = int(table[0][0]) + 1
            else:
                num = 1

            program_id = 'p' + str(num)
            print('program_id = ', program_id)

            #insert program data
            statement = "INSERT INTO programs (program_id, program_name, program_description, program_availability) VALUES (%s, %s, %s, %s);"
            params = [program_id, data['program_name'], data['program_description'], data['program_availability']]

            cursor.execute(statement, params)

            # setting up user program status based on program availability
            if data['program_availability'] == 'all':
                user_pgm_status= 'available'
            else:
                user_pgm_status = 'locked'

            #extracting all present students
            statement = "SELECT user_id FROM users WHERE user_status='student';"
            cursor.execute(statement)
            table = cursor.fetchall()

            # insert into program status, each user's corresponding status info
            for row in table:
                statement = "INSERT INTO program_status (user_id, program_id, user_program_status) VALUES (%s, %s, %s);"
                params = [row[0], program_id, user_pgm_status]
                cursor.execute(statement, params)

            cursor.execute('COMMIT')

            return (True, program_id)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


def delete_program(program_id):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('BEGIN')

            # remove program from programs table
            statement = "DELETE FROM programs WHERE program_id = %s;"
            cursor.execute(statement, [program_id])

            # find modules in program
            statement = "SELECT module_id FROM modules WHERE program_id = %s;"
            cursor.execute(statement, [program_id])
            table = cursor.fetchall()

            modules = []
            for row in table:
                modules.append(row[0])

            # remove program from modules table
            statement = "DELETE FROM modules WHERE program_id = %s;"
            cursor.execute(statement, [program_id])

            # remove program from program status
            statement = "DELETE FROM program_status WHERE program_id = %s;"
            cursor.execute(statement, [program_id])

            # remove program's relevant modules from assessment status
            for module_id in modules:
                statement = "DELETE FROM assessment_status WHERE module_id = %s;"
                cursor.execute(statement, [module_id])

            cursor.execute('COMMIT')

            return (True, "deleted program successfully")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


def insert_module(data):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            #check for missing arguments
            for key, value in data.items():
                if value is None or value == '':
                    raise Exception("missing " + str(key))

            cursor.execute('BEGIN')

            # check for duplicates for module name
            statement = "SELECT FROM modules WHERE module_name = %s AND modules.program_id = %s;"
            cursor.execute(statement, [data['module_name'], data['program_id']])
            table = cursor.fetchall()
            if len(table) != 0:
                raise Exception("module name conflict, insertion aborted")


            # generate module id
            statement = """SELECT substring(module_id FROM '\d+')
            from modules ORDER BY substring(module_id FROM '\d+')::INTEGER
            DESC limit 1 """
            cursor.execute(statement)
            table = cursor.fetchall()

            if len(table) != 0:
                num = int(table[0][0]) + 1
            else:
                num = 1
            module_id = 'm' + str(num)

            # get module index
            statement = "SELECT COUNT(module_id) FROM modules WHERE modules.program_id=%s;"
            cursor.execute(statement, [data['program_id']])
            table = cursor.fetchall()
            module_index = table[0][0]+1

            # insert module info into modules table
            statement = "INSERT INTO modules (module_id, program_id, module_name, content_type, content_link, module_index) VALUES (%s, %s, %s, %s, %s, %s);"
            params = [module_id, data['program_id'], data['module_name'], data['content_type'], data['content_link'], module_index]
            cursor.execute(statement, params)

            # if the module is an assessment, update user assessment status
            if data['content_type'] == "assessment":
                statement = "SELECT user_id FROM users WHERE user_status='student';"
                cursor.execute(statement)
                table = cursor.fetchall()
                for row in table:
                    statement = "INSERT INTO assessment_status (user_id, module_id, user_assessment_status) VALUES (%s, %s, %s); "
                    # default of 0 = incomplete
                    params = [row[0], module_id, 0]
                    cursor.execute(statement, params)

            cursor.execute('COMMIT')
            return (True, module_id)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)



def delete_module(module_id):
    #print("modify_database.py: delete_module", module_id)
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('BEGIN')

            # get module index and program id
            statement = "SELECT module_index, program_id, content_type FROM modules WHERE module_id = %s;"
            cursor.execute(statement, [module_id])
            table = cursor.fetchall()

            if len(table) == 0:
                raise Exception("no module of that module id in database, aborted")
            module_index = table[0][0]
            program_id = table[0][1]
            content_type = table[0][2]
            print('program_id, module_index, content_type', program_id, module_index, content_type)

            # delete row modules table
            statement = "DELETE FROM modules WHERE module_id = %s;"
            cursor.execute(statement, [module_id])

            # get list of module_ids to update indices
            statement = "SELECT module_id, module_index FROM modules WHERE program_id = %s AND module_index > %s;"
            cursor.execute(statement, [program_id, module_index])
            table = cursor.fetchall()

            modules = []
            for row in table:
                module_row = {}
                module_row['module_id'] = row[0]
                module_row['module_index'] = row[1]
                modules.append(module_row)

            # update module indices to make sure they're adjacent
            for module in modules:
                statement = "UPDATE modules SET module_index = %s WHERE module_id = %s;"
                cursor.execute(statement, [module['module_index']-1, module['module_id']])

            # delete module from assessment status table
            if content_type == 'assessment':
                statement = "DELETE FROM assessment_status WHERE module_id = %s;"
                cursor.execute(statement, [module_id])

            cursor.execute('COMMIT')
            return (True, "module successfully deleted")


    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


#
def update_program_name(program_id, new_program_name):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            #check for missing arguments
            if program_id is None or program_id == '':
                raise Exception("missing program id")
            if new_program_name is None or new_program_name =='':
                raise Exception("missing program name")


            #! check for duplicates via program name
            statement = "SELECT FROM programs WHERE program_name = %s;"
            cursor.execute(statement, [new_program_name])
            table = cursor.fetchall()
            if len(table) != 0:
                raise Exception("program name conflict, update aborted")

            cursor.execute('BEGIN')

            statement = "UPDATE programs SET program_name=%s WHERE program_id = %s;"
            cursor.execute(statement, [new_program_name, program_id])

            cursor.execute('COMMIT')
            return (True, "program name updated")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


def update_program_description(program_id, new_program_description):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #check for missing arguments
            if program_id is None or program_id == '':
                raise Exception("missing program id")
            if new_program_description is None or new_program_description =='':
                raise Exception("missing program description")

            cursor.execute('BEGIN')

            statement = "UPDATE programs SET program_description=%s WHERE program_id=%s;"
            cursor.execute(statement, [new_program_description, program_id])

            cursor.execute('COMMIT')
            return (True, "program description updated")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def update_program_availability(program_id, new_program_availability):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #check for missing arguments
            if program_id is None or program_id == '':
                raise Exception("missing program id")
            if new_program_availability is None or new_program_availability =='':
                raise Exception("missing program availability")

            cursor.execute('BEGIN')

            statement = "UPDATE programs SET program_availability=%s WHERE program_id=%s;"
            cursor.execute(statement, [new_program_availability, program_id])

            cursor.execute('COMMIT')
            return (True, "program availability updated")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


def update_module_name(program_id, module_id, new_module_name):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            #check for missing arguments
            if program_id is None or program_id == '':
                raise Exception("missing program id")
            if module_id is None or module_id == '':
                raise Exception("missing module id")
            if new_module_name is None or new_module_name =='':
                raise Exception("missing module name")

            # check for duplicates for module name
            statement = "SELECT FROM modules WHERE module_name = %s AND modules.program_id = %s;"
            cursor.execute(statement, [new_module_name, program_id])
            table = cursor.fetchall()
            if len(table) != 0:
                raise Exception("module name conflict, update aborted")

            cursor.execute('BEGIN')

            statement = "UPDATE modules SET module_name=%s WHERE module_id= %s;"

            cursor.execute(statement, [new_module_name, module_id])

            cursor.execute('COMMIT')
            return (True, "module name successfully updated")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def update_module_content_type(module_id, new_content_type):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            if module_id is None or module_id == '':
                raise Exception("missing module id")
            if new_content_type is None or new_content_type =='':
                raise Exception("missing content type")

            if new_content_type != 'assessment' and new_content_type != 'text':
                raise Exception('module content type must be assessment or text')
            cursor.execute('BEGIN')

            statement = "UPDATE modules SET content_type= %s WHERE module_id= %s;"
            cursor.execute(statement, [new_content_type, module_id])

            #update user assessment status
            if new_content_type == 'assessment':
                statement = "SELECT user_id FROM users WHERE user_status='student';"
                cursor.execute(statement)
                table = cursor.fetchall()
                for row in table:
                    statement = "INSERT INTO assessment_status (user_id, module_id, user_assessment_status) VALUES (%s, %s, %s); "
                    # default of 0 = incomplete
                    params = [row[0], module_id, 0]
                    cursor.execute(statement, params)
            else:
                statement = "DELETE FROM assessment_status WHERE module_id=%s;"
                cursor.execute(statement, [module_id])


            cursor.execute('COMMIT')
            return (True, "module content type updated")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def update_module_content_link(module_id, new_content_link):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            if module_id is None or module_id == '':
                raise Exception("missing module id")
            if new_content_link is None or new_content_link =='':
                raise Exception("missing content link")

            cursor.execute('BEGIN')

            statement = "UPDATE modules SET content_link= %s WHERE module_id= %s;"
            cursor.execute(statement, [new_content_link, module_id])

            cursor.execute('COMMIT')
            return (True, "module content link updated")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


## please do not use, should not be used on its own
## should only be used by edit_module_seq in oea
def update_module_index(module_id, new_module_index):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            if module_id is None or module_id == '':
                raise Exception("missing module id")
            if new_module_index is None or new_module_index =='':
                raise Exception("missing module index")

            cursor.execute('BEGIN')

            statement = "UPDATE modules SET module_index= %s WHERE module_id= %s;"
            cursor.execute(statement, [new_module_index, module_id])

            cursor.execute('COMMIT')
            return (True, "successfully changed module index")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def update_program_status(student_id, program_id, new_program_status):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            if student_id is None or student_id == '':
                raise Exception("missing student id")
            if program_id is None or program_id == '':
                raise Exception("missing program id")
            if new_program_status is None or new_program_status =='':
                raise Exception("missing program status")

            cursor.execute('BEGIN')

            statement = "UPDATE program_status SET user_program_status = %s WHERE user_id=%s AND program_id=%s;"
            cursor.execute(statement, [new_program_status, student_id, program_id])

            cursor.execute('COMMIT')
            return (True, "assessment status updated")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def update_assessment_status(student_id, module_id, new_assessment_status):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            if student_id is None or student_id == '':
                raise Exception("missing student id")
            if module_id is None or module_id == '':
                raise Exception("missing module id")
            if new_assessment_status is None or new_assessment_status =='':
                raise Exception("missing assessment status")

            cursor.execute('BEGIN')

            statement = "UPDATE assessment_status SET user_assessment_status = %s WHERE user_id=%s AND module_id=%s;"
            cursor.execute(statement, [new_assessment_status, student_id, module_id])

            cursor.execute('COMMIT')
            return (True, "assessment status updated")

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

#---------------------------------------------
# ACCESSING DATABASE
# --------------------------------------------

def is_admin_authorized(username):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #print("database: is_admin_authorized", username)
            statement = "SELECT * FROM users where user_status = 'admin' AND user_email=%s;"
            cursor.execute(statement, [username])
            table = cursor.fetchall()

            return (True, len(table)!=0)
    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


def is_student_authorized(username):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #print("database: is_student_authorized", username)
            statement = "SELECT * FROM users where user_status = 'student' AND user_email=%s;"
            cursor.execute(statement, [username])
            table = cursor.fetchall()

            return (True, len(table)!=0)
    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def get_student_info(user_email):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            if user_email is None or user_email == '':
                raise Exception("missing user email")

            statement = "SELECT * FROM users WHERE user_status = 'student' AND user_email=%s;"
            cursor.execute(statement, [user_email])
            table = cursor.fetchall()

            if len(table) == 0:
                raise Exception("student not in database")

            student = table[0]

            student_info = {}
            student_info['user_id'] = student[0]
            student_info['user_name'] = student[1]
            student_info['user_email'] = student[2]


            statement = "SELECT program_id, user_program_status FROM program_status WHERE user_id=%s;"
            cursor.execute(statement, [student_info['user_id']])
            table = cursor.fetchall()

            available_programs = []
            locked_programs = []
            enrolled_programs = []

            for row in table:
                program_id = row[0]
                user_program_status = row[1]

                statement = "SELECT program_name, program_description FROM programs WHERE program_id = %s;"
                cursor.execute(statement, [program_id])
                program_table = cursor.fetchall()
                if len(program_table) == 0:
                    raise Exception("empty program in program_status when looking for student info")
                program_name = program_table[0][0]
                program_description = program_table[0][1]

                program_info = {}
                program_info['program_id'] = program_id
                program_info['program_name'] = program_name
                program_info['program_description'] = program_description
                if user_program_status == 'available' :
                    available_programs.append(program_info)
                elif user_program_status == 'locked':
                    locked_programs.append(program_info)
                elif user_program_status == 'enrolled':
                    enrolled_programs.append(program_info)

            student_info['available_programs'] = available_programs
            student_info['locked_programs'] = locked_programs
            student_info['enrolled_programs'] = enrolled_programs

            return (True, student_info)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


def get_all_admins():
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #print("access_database.py: get_all_students:")
            statement = "SELECT * FROM users WHERE user_status='admin';"

            cursor.execute(statement)
            table = cursor.fetchall()

            # list of dictionaries of programs
            admins = []
            for row in table:
                admin_row = {}
                admin_row['user_id'] = row[0]
                admin_row['user_name'] = row[1]
                admin_row['user_email'] = row[2]
                admins.append(admin_row)

            #print("success access_database.py: get_all_admins")
            return (True, admins)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def get_all_students():
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #print("access_database.py: get_all_students:")
            statement = "SELECT * FROM users WHERE user_status='student';"

            cursor.execute(statement)
            table = cursor.fetchall()

            # list of dictionaries of programs
            students = []
            for row in table:
                student_row = {}
                student_row['user_id'] = row[0]
                student_row['user_name'] = row[1]
                student_row['user_email'] = row[2]
                students.append(student_row)
            return (True, students)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


def get_all_programs():
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            #print("access_database.py: get_programslist")
            statement = "SELECT * FROM programs;"
            cursor.execute(statement)
            table = cursor.fetchall()

            # list of list of dictionaries of programs
            programs = []
            for row in table:
                program_row = {}
                program_row['program_id'] = row[0]
                program_row['program_name'] = row[1]
                program_row['program_description'] = row[2]
                program_row['program_availability'] = row[3]
                programs.append(program_row)

            #print("success access_database.py: get_programslist")
            return (True, programs)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)


def get_program_info(program_id):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            if program_id is None or program_id == '':
                raise Exception("missing program id")

            print(' program id in get program info =', program_id)
            statement = "SELECT * FROM programs WHERE program_id=%s;"
            cursor.execute(statement, [program_id])
            table = cursor.fetchall()

            if len(table) == 0:
                raise Exception("no such program exists in database")

            program_info = {}
            program_info['program_id'] = table[0][0]
            program_info['program_name'] = table[0][1]
            program_info['program_description'] = table[0][2]
            program_info['program_availability'] = table[0][3]

            # get program modules
            statement = "SELECT * FROM modules WHERE modules.program_id=%s;"
            cursor.execute(statement, [program_id])
            table = cursor.fetchall()

            # list of dictionaries of modules within program
            modules = []
            for row in table:
                module_row = {}
                module_row['module_id'] = row[0]
                module_row['program_id'] = row[1]
                module_row['module_name'] = row[2]
                module_row['content_type'] = row[3]
                module_row['content_link'] = row[4]
                module_row['module_index'] = row[5]
                modules.append(module_row)

            #sort modules via index
            modules = sorted(modules, key=lambda x:x['module_index'])
            program_info['modules'] = modules

            # print("success access_database.py: get_program_modules")
            return (True, program_info)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def get_module_info(module_id):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            if module_id is None or module_id == '':
                raise Exception("missing module id")

            statement = "SELECT * FROM modules WHERE module_id=%s;"
            cursor.execute(statement, [module_id])
            table = cursor.fetchall()

            if len(table) == 0:
                raise Exception("no such module id in modules table")

            module_info = {}
            module_info['module_id'] = table[0][0]
            module_info['program_id'] = table[0][1]
            module_info['module_name'] = table[0][2]
            module_info['content_type'] = table[0][3]
            module_info['content_link'] = table[0][4]
            module_info['module_index'] = table[0][5]

            return (True, module_info)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def get_student_program_status(student_id, program_id):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            if student_id is None or student_id == '':
                raise Exception("missing student id")
            if program_id is None or program_id == '':
                raise Exception("missing program id")

            statement = "SELECT user_program_status FROM program_status WHERE user_id=%s AND program_id=%s;"
            cursor.execute(statement, [student_id, program_id])
            table = cursor.fetchall()
            if len(table) == 0:
                raise Exception("user program status not in database")
            return (True, table[0][0])

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)

def get_student_enrolled_program_info(student_id):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            if student_id is None or student_id == '':
                raise Exception("missing student id")

            statement = "SELECT programs.program_id, program_name FROM programs, program_status WHERE user_id=%s AND programs.program_id=program_status.program_id AND user_program_status='enrolled';"
            cursor.execute(statement, [student_id])
            table = cursor.fetchall()


            enrolled_programs = []
            for row in table:
                enrolled_program = {}
                enrolled_program['program_id'] = row[0]
                enrolled_program['program_name'] = row[1]

                # get program progress
                statement = "SELECT SUM(user_assessment_status), COUNT(user_assessment_status) FROM modules, assessment_status WHERE user_id=%s AND modules.program_id=%s AND modules.module_id=assessment_status.module_id;"
                cursor.execute(statement, [student_id, enrolled_program['program_id']])
                status_table = cursor.fetchall()
                # print("status table:", status_table)

                assessment_completion = status_table[0][0]
                assessment_total = status_table[0][1]
                program_progress = str(assessment_completion) + "/" + str(assessment_total)
                if assessment_completion is None:
                    program_progress = "N/A"
                print("program_progress", program_progress)
                enrolled_program['program_progress'] = program_progress


                statement = "SELECT modules.module_id, module_name, user_assessment_status, modules.module_index FROM modules, assessment_status WHERE user_id=%s AND modules.program_id=%s AND modules.module_id=assessment_status.module_id;"

                cursor.execute(statement, [student_id, enrolled_program['program_id']])
                module_table = cursor.fetchall()

                program_assessments = []
                for module_row in module_table:
                    program_assessment = {}
                    program_assessment['module_id'] = module_row[0]
                    program_assessment['module_name'] = module_row[1]
                    program_assessment['user_assessment_status'] = module_row[2]
                    program_assessment['module_index'] = module_row[3]
                    program_assessments.append(program_assessment)
                program_assessments = sorted(program_assessments, key=lambda x:x['module_index'])
                enrolled_program['program_assessments'] = program_assessments


                enrolled_programs.append(enrolled_program)

            return (True, enrolled_programs)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)
#
def get_locked_index(user_id, program_id):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:

            if user_id is None or user_id == '':
                raise Exception("missing user id")
            if program_id is None or program_id == '':
                raise Exception("missing program id")

            statement = "SELECT MIN(module_index) FROM modules, assessment_status WHERE user_assessment_status='0' AND content_type='assessment' AND assessment_status.user_id=%s AND modules.program_id=%s AND assessment_status.module_id=modules.module_id;"
            cursor.execute(statement, [user_id, program_id])
            table = cursor.fetchall()

            if table[0][0] is None: #no incomplete assessment found
                module_index = 10000
            else:
                module_index = table[0][0]

            print("locked_index", module_index)

            return (True, module_index)

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)



def get_student_program_progress(student_id, program_id):

    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            if student_id is None or student_id == '':
                raise Exception("missing student id")
            if program_id is None or program_id == '':
                raise Exception("missing program id")

            statement = "SELECT SUM(user_assessment_status), COUNT(user_assessment_status) FROM modules, assessment_status WHERE user_id=%s AND program_id=%s AND modules.module_id=assessment_status.module_id;"
            cursor.execute(statement, [student_id, program_id])

            table = cursor.fetchall()
            assessment_completion = table[0][0]
            assessment_total = table[0][1]
            program_progress = str(assessment_completion) + "/" + str(assessment_total)
            return (True, program_progress)

    except Exception as error:

        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, str(error))
    finally:
        _put_connection(connection)



def main():
    print(get_student_enrolled_program_info(2))

    # print(get_locked_index('p1',2))
    # update_program_status(2, 'p1', 'enrolled')
    # print("done upating")
    # print(get_student_enrolled_program_info(2))
    # print(get_student_program_progress(2, 'p1'))

    # program1_id = 'p1'

    # module4_name = 'p1 assessment2' # module 1 not a typo
    # module4_content_type = "assessment"
    # module4_content_link = 'module4 link'

    # module4_data = {
    #     'program_id': program1_id,
    #     'module_name': module4_name,
    #     'content_type': module4_content_type,
    #     'content_link': module4_content_link,
    # }


    # insert_module(module4_data)
    # print("main: insert module4")

    # print(get_all_admins())
    # success, programs_list = get_all_programs()
    # print('list of programs =', programs_list)

    # program_id = 'p1'
    # program_details = get_program_details(program_id)
    # print('Getting program_details = ', program_details)

    # print(get_student_info('student1oea@gmail.com'))

    # ----------------------------------------- #
    # admin_data = {}
    # admin_data['admin_email'] = 'oeadevuser@gmail.com'
    # admin_data['admin_name'] = 'oeadevuser'
    # insert_admin(admin_data)


    # student_data = {}
    # student_data['student_email'] = 'student1oea@gmail.com'
    # student_data['student_name'] = 'student1oea'
    # insert_student(student_data)

    # ------------------------------------------- #
    # delete_user(1)
    # delete_user(2)
    # delete_user(3)

    #-------------------------------------------#

    # create new program: Tree Ambassador 101
    # program1_data = {
    #                 "program_name": "Tree Ambassador 101",
    #                 "program_description": "Description",
    #                 "program_availability": "all"
    #                 }
    # print('data: ', program1_data)
    # insert_program(program1_data)
    # print("main: insert program1")

    # -------------------------------------------
    # insert module 1 of tree ambassador 101
    # program1_id = 'p1'
    # module1_name = 'M1 Instructions'
    # module1_content_type = "text"
    # module1_content_link = 'https://docs.google.com/document/d/1PP-GiTqVcvJYpqVUxQ_bXSsru6H200l39RovL0AhYgw/edit?usp=sharing'
    # module1_data = {
    #     'program_id': program1_id,
    #     'module_name': module1_name,
    #     'content_type': module1_content_type,
    #     'content_link': module1_content_link,
    # }


    # insert_module(module1_data)
    # print("main: insert module1")


    # success, num = get_num_modules_in_program('p1')
    # print("num of modules:", num)
    # delete_module('m1')

    # insert module 2 of tree ambassador 101
    # program1_id = 'p1'
    # module2_name = 'Module 1 Learning Exercise' # module 1 not a typo
    # module2_content_type = "assessment"
    # module2_content_link = 'https://docs.google.com/forms/d/e/1FAIpQLScGFPXzgFiIaIc5R7NQW_OvINY7y7xc4UHHhIIkt-4AJ-TZoQ/viewform'
    # module2_index = 1 # need a function to get index


    # module2_data = {
    #     'program_id': program1_id,
    #     'module_name': module2_name,
    #     'content_type': module2_content_type,
    #     'content_link': module2_content_link,
    # }


    # insert_module(module2_data)
    # print("main: insert module2")

    # delete_program('(t,p1)')

    # update_program_name('p3', 'new amb tree')
    # update_program_description('p2', 'new description')
    # update_program_availability('p2', 'none')
    # update_module_name('m3', "mod 1 new name")
    # update_module_index('m3', '1')
    # update_assessment_status(2,'m2', 1)

if __name__ == '__main__':
    main()
