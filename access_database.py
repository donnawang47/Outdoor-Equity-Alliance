import psycopg2
import sys
import os

DATABASE_URL = os.getenv('DATABASE_URL')
CONN = psycopg2.connect("dbname=oea user=postgres password=xxx")

# get list of programs for a student
# should be divided into three categories
# EXTREME WIPPPP!!
def get_student_programs(student_id):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                programs = get_all_programs()

                params = []
                program_list_str = '' #account for first program_id, shouldnt have comma in front
                for program in programs:
                     params.append(program['program_id'])
                     #make program_list_str
                     program_list_str += ','+program['program_id']

                stmt_str = "SELECT %s FROM students WHERE "
                stmt_str += "students.student_id LIKE %s"

                cursor.execute(stmt_str, [program_list_str, student_id])
                table = cursor.fetchall()
                # for row in table:
                #     print(row)

                data = {}

                available = []
                locked = []
                enrolled = []
                index = 0

                row = table[0]
                for program in programs: #program_id specifically
                    if(row[index] == 'available'):
                         available.append[program]
                    elif row[index] == 'locked':
                         locked.append[program]
                    elif row[index] == 'enrolled':
                         enrolled.append[program]
                    index += 1

                data['available'] = available
                data['locked'] = locked
                data ['enrolled'] = enrolled
                return data

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)

# get complete list of programs
# divided into three(?) categories
def get_all_programs():
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                stmt_str = "SELECT * FROM programs "

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
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)
            return (False, err_msg)

# given a program_id, get all modules within that program
def get_program_modules(program_id):
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                stmt_str = "SELECT * FROM programs, modules WHERE "
                stmt_str += "programs.program_id=modules.program_id "
                stmt_str += "AND modules.program_id LIKE %s"

                cursor.execute(stmt_str, [program_id])
                table = cursor.fetchall()
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
                return (True, data)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)
            return (False, err_msg)

# get complete list of students
# with some information??
def get_all_students():
    try:
        with CONN as connection:
        # with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                stmt_str = "SELECT * FROM students "

                cursor.execute(stmt_str)
                table = cursor.fetchall()

                # list of dictionaries of programs
                data = []
                for row in table:
                    data_row = {}
                    data_row['student_id'] = row[0]
                    data_row['student_name'] = row[1]
                    data_row['student_email'] = row[2]
                    #check if the column name method works
                    data.append(data_row)

                return (True, data)

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)
            return (False, err_msg)



# for testing
def main():
    programs = get_all_programs()
    # print(programs)
    print("Display programs list for admin: ")
    print("------------------------------------------------------")
    for program in programs:
        print("Program name:", program['program_name'])
        print("Program description:", program['description'])
        print("Program availability:", program['program_availability'])
        print("------------------------------------------------------")

    print("Display modules for Tree Ambassador 101")
    # how are we going to get id
    program_id = 'P1'
    modules = get_program_modules(program_id)

    print("Program name:", modules['program_name'])
    print("Program description:", modules['description'])
    print("Program availability:", modules['program_availability'])
    for module in modules['modules']:
        print("MODULE:", module['module_name'], module['content_type'], module['content_link'], module['module_index'])
    print("------------------------------------------------------")

    print("Display modules for LOCKED PROGRAM")
    # how are we going to get id
    program_id = 'P2'
    modules = get_program_modules(program_id)
    print("Program name:", modules['program_name'])
    print("Program description:", modules['description'])
    print("Program availability:", modules['program_availability'])
    for module in modules['modules']:
        print("MODULE:", module['module_name'], module['content_type'], module['content_link'], module['module_index'])
    print("------------------------------------------------------")

if __name__ == '__main__':
    main()
