import psycopg2
import sys
import os
import queue

#export DATABASE_URL=postgres://oea_user:KTYMB7UGGi1I8wXjXAFr3vvqNbl5lN4X@dpg-cgp3bg0u9tun42rpj98g-a.oregon-postgres.render.com/oea

# for windows powershell: run this command
# $env:DATABASE_URL="postgres://oea_user:KTYMB7UGGi1I8wXjXAFr3vvqNbl5lN4X@dpg-cgp3bg0u9tun42rpj98g-a.oregon-postgres.render.com/oea"
# for windows cmd: set DATABASE_URL=postgres://oea_user:KTYMB7UGGi1I8wXjXAFr3vvqNbl5lN4X@dpg-cgp3bg0u9tun42rpj98g-a.oregon-postgres.render.com/oea

# this always works i think
# _database_url = 'postgres://oea_user:KTYMB7UGGi1I8wXjXAFr3vvqNbl5lN4X@dpg-cgp3bg0u9tun42rpj98g-a.oregon-postgres.render.com/oea'

_database_url = os.getenv('DATABASE_URL')
_connection_pool = queue.Queue()

def _get_connection():
    try:
        conn = _connection_pool.get(block=False)
    except queue.Empty:
        print('DATABASE_URL =',_database_url)
        conn = psycopg2.connect(_database_url)
    return conn

def _put_connection(conn):
    _connection_pool.put(conn)

# -----------------------------------------------------------
#admin

# get complete list of programs
# divided into three(?) categories
def get_programslist():
    connection = _get_connection()
    try:
        # with CONN as connection:
        with connection.cursor() as cursor:
            print("access_database.py: get_programslist")
            stmt_str = "SELECT * FROM programs;"

            cursor.execute(stmt_str)
            table = cursor.fetchall()

            # list of dictionaries of programs
            data = []
            for row in table:
                data_row = {}
                data_row['program_id'] = row[0]
                data_row['program_name'] = row[1]
                data_row['description'] = row[2]
                data_row['program_availability'] = row[3]
                data.append(data_row)

            print("success access_database.py: get_programslist")
            return (True, data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def get_program_details(program_id):
    connection = _get_connection()
    try:
        # with CONN as connection:
        with connection.cursor() as cursor:
            print("In access_database.py: get_program_details")
            # print("in get pgm modules", program_id)
            stmt_str = "SELECT * FROM programs WHERE "
            stmt_str += "program_id=%s"
            # stmt_str += "ORDER BY program_id ASC, module_id ASC;"

            cursor.execute(stmt_str, [program_id])

            table = cursor.fetchall()
            #print("table:", table)
            # for row in table:
            #     print(row)
            data = {}
            data['program_id'] = table[0][0]
            data['program_name'] = table[0][1]
            data['description'] = table[0][2]
            data['program_availability'] = table[0][3]
            print('Program info', data)

            # get program modules
            stmt_str = "SELECT * FROM programs, modules WHERE "
            stmt_str += "programs.program_id=modules.program_id "
            stmt_str += "AND modules.program_id LIKE %s "
            # stmt_str += "ORDER BY program_id ASC, module_id ASC;"

            cursor.execute(stmt_str, [program_id])
            table = cursor.fetchall()
            print("Modules of program", table)

            # # list of dictionaries of modules within program
            modules = []
            for row in table:
                modules_row = {}
                modules_row['module_id'] = row[4]
                # row[5] is program_id
                modules_row['module_name'] = row[6]
                modules_row['content_type'] = row[7]
                modules_row['content_link'] = row[8]
                modules_row['module_index'] = row[9]
                modules.append(modules_row)

                #sort modules via index
            modules = sorted(modules, key=lambda x:x['module_index'])
            data['modules'] = modules
            # print('modules', modules)
            # print("data", data)
            # print("success access_database.py: get_program_modules")
            return (True, data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)



def get_module(module_id):
    #module_id TEXT, program_id TEXT, module_name TEXT, content_type TEXT, content_link TEXT, module_index INTEGER
    connection = _get_connection()
    try:
        # with CONN as connection:
        with connection.cursor() as cursor:
            print("access_database.py: get_module:", module_id)
            stmt_str = "SELECT * FROM modules WHERE "
            stmt_str += "modules.module_id LIKE %s;"

            cursor.execute(stmt_str, [module_id])
            print(stmt_str)
            table = cursor.fetchall()
            print("table:", table)
            # for row in table:
            #     print(row)


            data = {}
            data['module_id'] = table[0][0]
            data['program_id'] = table[0][1]
            data['module_name'] = table[0][2]
            data['content_type'] = table[0][3]
            data['content_link'] = table[0][4]
            data['module_index'] = table[0][5]
            print("data", data)
            print("success access_database.py: get_module:", module_id)
            return (True, data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def get_student_info(student_id):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            print("access_database.py: get_student_info:", student_id)
            list_stmt = """
                SELECT column_name FROM information_schema.columns where table_name = 'users' ORDER BY ordinal_position;"""
            cursor.execute(list_stmt)

            columns = cursor.fetchall()

            stmt_str = "SELECT * FROM users WHERE user_status = 'student' AND user_id=%s;"
            cursor.execute(stmt_str, [student_id])
            data = cursor.fetchall()
            print(data)
            #data[0] because should only be one row of data

            student_data = {}
            available_pgms = []
            locked_pgms = []
            enrolled_pgms = []
            for index, column in enumerate(columns):
                print("column", column)
                # categorize student programs
                if 'p' in column[0]: #is a program
                    p_status = data[0][index]
                    success, pgm_details = get_program_details(column[0])
                    if success:
                        if p_status == 'available' :
                            available_pgms.append(pgm_details)
                        elif p_status == 'locked':
                            locked_pgms.append(pgm_details)
                        elif p_status == 'enrolled':
                            enrolled_pgms.append(pgm_details)
                    # error handle
                else:
                    student_data[column[0]] = data[0][index]
                    print(student_data[column[0]], data[0][index])

            student_data['Available Programs'] = available_pgms
            #print("available_pgms", available_pgms)
            student_data['Locked Programs'] = locked_pgms
            #print("locked_pgms", locked_pgms)
            student_data ['Enrolled Programs'] = enrolled_pgms
            #print("enrolled_pgms", enrolled_pgms)

            print("student_data:", student_data)
            print("success access_database.py: get_student_info:", student_id)
            return (True, student_data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def is_admin_authorized(username):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            print("access_database: is_admin_authorized", username)
            stmt_str = "SELECT * FROM users where user_status = 'admin' AND user_email=%s;"
            cursor.execute(stmt_str, [username])
            data = cursor.fetchall()

            return (True, len(data)!=0)
    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)


def is_student_authorized(username):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            print("access_database: is_student_authorized", username)
            stmt_str = "SELECT * FROM users where user_status = 'student' AND user_email=%s;"
            cursor.execute(stmt_str, [username])
            data = cursor.fetchall()

            return (True, len(data)!=0)
    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

def get_student_id(username):
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            print("access_database: get_student_id", username)
            stmt_str = "SELECT * FROM users WHERE user_status= 'student' AND user_email=%s;"
            cursor.execute(stmt_str, [username])
            data = cursor.fetchall()

            if len(data) == 0:
                raise Exception("username not in database")

            return (True, data[0][0])
    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)


def get_all_admins():
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            print("access_database.py: get_all_students:")
            stmt_str = "SELECT * FROM users WHERE user_status='admin';"

            cursor.execute(stmt_str)
            table = cursor.fetchall()

            # list of dictionaries of programs
            data = []
            for row in table:
                data_row = {}
                data_row['admin_id'] = row[0]
                data_row['admin_name'] = row[1]
                data_row['admin_email'] = row[2]
                data_row['admin_status'] = row[3]
                #check if the column name method works
                data.append(data_row)
            print("data:", data)
            print("success access_database.py: get_all_admins")
            return (True, data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

# get complete list of students
# with some information??
def get_all_students():
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            print("access_database.py: get_all_students:")
            stmt_str = "SELECT * FROM users WHERE user_status='student';"

            cursor.execute(stmt_str)
            table = cursor.fetchall()

            # list of dictionaries of programs
            data = []
            for row in table:
                data_row = {}
                data_row['student_id'] = row[0]
                data_row['student_name'] = row[1]
                data_row['student_email'] = row[2]
                data_row['student_status'] = row[3]
                #check if the column name method works
                data.append(data_row)
            print("data:", data)
            print("success access_database.py: get_all_students")
            return (True, data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)
    finally:
        _put_connection(connection)

# get list of programs for a student
# should be divided into three categories
def get_student_programs(student_id):
    print("access_database.py: get_student programs (no database)")
    status, student_info = get_student_info(student_id)
    print(student_info)
    if not status:
        return status, student_info


    data = {}

    available = []
    locked = []
    enrolled = []

    # for key in student_info: #program_id specifically
    #     print("key", key)
    #     if 'p' in key: #is a program
    #         p_status = student_info[key]
    #         if p_status == 'available' :
    #             available.append(key)
    #         elif p_status == 'locked':
    #             locked.append(key)
    #         elif p_status == 'enrolled':
    #             enrolled.append(key)

    for program in student_info['Available Programs']:
        available.append(program['program_id'])
    for program in student_info['Locked Programs']:
        locked.append(program['program_id'])
    for program in student_info['Enrolled Programs']:
        enrolled.append(program['program_id'])

    data['Available'] = available
    data['Locked'] = locked
    data ['Enrolled'] = enrolled
    print("data", data)
    print("success access_database.py: get_student programs (no database)")
    return status, data

def get_student_program_status(student_id, program_id):
    status, student_info = get_student_programs(student_id)
    if status:
        if program_id in student_info['Available']:
            return status, "available"
        elif program_id in student_info['Locked']:
            return status, "locked"
        elif program_id in student_info['Enrolled']:
            return status, "enrolled"
    else:
        return status, student_info

# helper function
# returns number of student_id's completed assessments
def get_student_module_completion(student_id, assessment_ids):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            #print(module_ids[0])
            print("access_database.py: get_student_module_completion:", student_id, assessment_ids)
            stmt_str = "SELECT SUM( users." + assessment_ids[0]
            for i in range(1,len(assessment_ids)):
                #print(module_ids[1])
                stmt_str+= " + users." + assessment_ids[i]
            stmt_str += " ) FROM users WHERE user_id = %s"
            cursor.execute(stmt_str, [student_id])
            data = cursor.fetchall()

            print("num of completed assess:" , data[0][0])
            print("success access_database.py: get_student_module_completion")

            return (True, data[0][0])

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)

# index count starting at 1
def get_locked_module_index(studentid, programid):
    success, module_info = get_program_details(programid)
    print("get_student_pgm_prog get pgm modules done")
    modules = module_info['modules']
    # get min incomplete asssessment
    min_incomplete_idx = len(modules)
    print("total modules", min_incomplete_idx)
    if success:
        for module in modules:
            module_id = module['module_id']

            curr_idx = module['module_index']
            print("id:", module_id, "; type:", module['content_type'], "; curr_idx:", curr_idx )
            if module['content_type'] == 'assessment' and  curr_idx < min_incomplete_idx:

                success, complete = get_student_assessment_status(studentid, module_id)
                print(module_id, complete)
                # error handling
                if complete == 0:
                    min_incomplete_idx = curr_idx
                    print("min_incomplete_idx", min_incomplete_idx)

        return (True, min_incomplete_idx)
    return (False, "error")



# returns a fractional string indicating studentid progress of programid
def get_student_program_progress(studentid, programid):
    # get all moduleids for desired program
    print("access_database.py: get_student_program_progress (no database):", studentid, programid)
    success, module_info = get_program_details(programid)
    print("get_student_pgm_prog get pgm modules done")
    modules = module_info['modules']
    # only want modules w/ assessment type
    if success:
        assessment_ids = []
        for module in modules:
            print("id:", module['module_id'], "; type:", module['content_type'] )
            if module['content_type'] == 'assessment':
                assessment_ids.append(module['module_id'])
            # module_id = module['module_id']
            # get student completion of module_id
        print("for loop done:", assessment_ids)
        progress = "no assessment module for this program yet"
        if len(assessment_ids) != 0:
            success, completed_modules = get_student_module_completion(studentid, assessment_ids)
            if success:
                pgm_size = len(assessment_ids)
                progress = str(completed_modules) + "/" + str(pgm_size)
                print("student progress", progress)
        return (True, progress)
    return (False, "error")

# returns 1 if studnet completed assess
def get_student_assessment_status(studentid, assessmentid):
    connection = _get_connection()
    try:
        # with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            #print(module_ids[0])
            print("access_database.py: get_student_assessment_status:", studentid, assessmentid)
            stmt_str = "SELECT " + assessmentid + " FROM users WHERE "
            stmt_str += "user_id = %s"

            cursor.execute(stmt_str, [studentid])
            data = cursor.fetchall()

            print("data:" , data[0][0])
            print("success access_database.py: get_student_module_completion")

            return (True, data[0][0])

    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, error)
    finally:
        _put_connection(connection)

# for testing
def main():
    get_student_info('2')
    # get_locked_module_index('2', 'p4')
    # get_student_assessment_status('2', 'm2')
    # get_program_details('p3')
    # status, programs = get_all_programs()
    # # print(programs)
    # print("Display programs list for admin: ")
    # print("------------------------------------------------------")
    # for program in programs:
    #     print("Program ID: ", program['program_id'])
    #     print("Program name:", program['program_name'])
    #     print("Program description:", program['description'])
    #     print("Program availability:", program['program_availability'])
    #     print("------------------------------------------------------")

    # print("Display modules for Tree Ambassador 101")
    # # how are we going to get id
    # program_id = 'P1'
    # status, modules = get_program_modules(program_id)

    # # print("Program name:", modules['program_name'])
    # # print("Program description:", modules['description'])
    # # print("Program availability:", modules['program_availability'])
    # for module in modules['modules']:
    #     print("MODULE:", module['module_name'], module['content_type'], module['content_link'], module['module_index'])
    # # print("------------------------------------------------------")

    # # print("Display modules for Test - LOCKED PROGRAM")
    # # # how are we going to get id
    # # program_id = 'P2'
    # # status, modules = get_program_modules(program_id)
    # # print("Program name:", modules['program_name'])
    # # print("Program description:", modules['description'])
    # # print("Program availability:", modules['program_availability'])
    # # for module in modules['modules']:
    # #     print("MODULE:", module['module_name'], module['content_type'], module['content_link'], module['module_index'])
    # # print("------------------------------------------------------")

    # # print("---------STUDENTS-------------------------")
    # get_student_info(2)
    # # std_pg = get_student_programs(2)
    # # print(std_pg)

    # # # testing get student progress
    # program_id = 'p1'
    # status, modules = get_program_modules(program_id)
    # print(modules['modules'])
    # get_student_program_progress(2, program_id)
    # get_module("m1")

if __name__ == '__main__':
    main()
