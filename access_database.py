import psycopg2
import sys
import os

DATABASE_URL = os.getenv('DATABASE_URL')
CONN = psycopg2.connect("dbname=oea user=rmd password=xxx")

#admin

# get complete list of programs
# divided into three(?) categories
def get_programslist():
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
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

                return (True, data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)

# given a program_id, get all modules within that program
def get_program_modules(program_id):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                # print("in get pgm modules", program_id)
                stmt_str = "SELECT * FROM programs, modules WHERE "
                stmt_str += "programs.program_id=modules.program_id "
                stmt_str += "AND modules.program_id LIKE %s;"

                cursor.execute(stmt_str, [program_id])

                table = cursor.fetchall()
                # print("table:", table)
                # for row in table:
                #     print(row)

                data = {}
                data['program_id'] = table[0][0]
                data['program_name'] = table[0][1]
                data['description'] = table[0][2]
                data['program_availability'] = table[0][3]

                # list of dictionaries of modules within program
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

                data['modules'] = modules
                # print(modules)
                return (True, data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)

def get_student_info(student_id):
    try:
        with CONN as connection:
            with connection.cursor() as cursor:
                list_stmt = """
                    SELECT column_name FROM information_schema.columns where table_name = 'users' ORDER BY ordinal_position;"""
                cursor.execute(list_stmt)

                columns = cursor.fetchall()
                print(columns)
                # stored in format [('student_id',), ('student_name',), ('student_email',), ('p1',)... etc

                stmt_str = "SELECT * FROM users WHERE user_status = 'student' AND user_id=%s;"
                cursor.execute(stmt_str, [student_id])
                data = cursor.fetchall()
                #data[0] because should only be one row of data

                print("get_student_info:", data)

                student_data = {}
                for index, column in enumerate(columns):
                     student_data[column[0]] = data[0][index]

                return student_data


    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)

# get complete list of students
# with some information??
def get_all_students():
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                stmt_str = "SELECT * FROM users WHERE user_status=student;"

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

                return (True, data)

    except Exception as error:
        err_msg = "A server error occurred. "
        err_msg += "Please contact the system administrator."
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        return (False, err_msg)

# get list of programs for a student
# should be divided into three categories
def get_student_programs(student_id):
    # try:
    #     with CONN as connection:
    #     # with psycopg2.connect(DATABASE_URL) as connection:
    #         with connection.cursor() as cursor:

    #             # programs = get_all_programs()

    #             # params = []
    #             # program_list_str = '' #account for first program_id, shouldnt have comma in front
    #             # for program in programs:
    #             #      params.append(program['program_id'])
    #             #      #make program_list_str
    #             #      program_list_str += ','+program['program_id']

    #             # stmt_str = "SELECT %s FROM students WHERE "
    #             # stmt_str += "students.student_id LIKE %s;"

    #             # cursor.execute(stmt_str, [program_list_str, student_id])
    #             # table = cursor.fetchall()
    #             # # for row in table:
    #             # #     print(row)

    # except Exception as error:
    #     err_msg = "A server error occurred. "
    #     err_msg += "Please contact the system administrator."
    #     print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
    #     return (False, err_msg)

    student_info = get_student_info(student_id)
    print(student_info)

    data = {}

    available = []
    locked = []
    enrolled = []

    for key in student_info: #program_id specifically
        print("key", key)
        if 'p' in key: #is a program
            p_status = student_info[key]
            if p_status == 'available' :
                available.append(key)
            elif p_status == 'locked':
                locked.append(key)
            elif p_status == 'enrolled':
                enrolled.append(key)

    data['Available'] = available
    data['Locked'] = locked
    data ['Enrolled'] = enrolled
    return data

# helper function
# returns number of student_id's completed assessments
def get_student_module_completion(student_id, assessment_ids):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                #print(module_ids[0])
                stmt_str = "SELECT SUM( users." + assessment_ids[0]
                for i in range(1,len(assessment_ids)):
                    #print(module_ids[1])
                    stmt_str+= " + users." + assessment_ids[i]
                stmt_str += " ) FROM users WHERE user_id = %s"
                print(stmt_str)
                cursor.execute(stmt_str, [student_id])
                data = cursor.fetchall()

                print("num of completed assess:" , data[0][0])

                return (True, data[0][0])

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)
            return (False, err_msg)


# returns a fractional string indicating studentid progress of programid
def get_student_program_progress(studentid, programid):
    # get all moduleids for desired program
    print("in get std pgm prog")
    success, module_info = get_program_modules(programid)
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
        success, completed_modules = get_student_module_completion(studentid, assessment_ids)
        if success:
            pgm_size = len(assessment_ids)
            progress = str(completed_modules) + "/" + str(pgm_size)
            print("student progress", progress)
            return progress

# for testing
def main():
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

    print("Display modules for Tree Ambassador 101")
    # how are we going to get id
    program_id = 'P1'
    status, modules = get_program_modules(program_id)

    # print("Program name:", modules['program_name'])
    # print("Program description:", modules['description'])
    # print("Program availability:", modules['program_availability'])
    for module in modules['modules']:
        print("MODULE:", module['module_name'], module['content_type'], module['content_link'], module['module_index'])
    # print("------------------------------------------------------")

    # print("Display modules for Test - LOCKED PROGRAM")
    # # how are we going to get id
    # program_id = 'P2'
    # status, modules = get_program_modules(program_id)
    # print("Program name:", modules['program_name'])
    # print("Program description:", modules['description'])
    # print("Program availability:", modules['program_availability'])
    # for module in modules['modules']:
    #     print("MODULE:", module['module_name'], module['content_type'], module['content_link'], module['module_index'])
    # print("------------------------------------------------------")

    # print("---------STUDENTS-------------------------")
    # get_all_students()
    # print("Student 2 Programs")
    # get_student_info(2)
    # std_pg = get_student_programs(2)
    # print(std_pg)

if __name__ == '__main__':
    main()
