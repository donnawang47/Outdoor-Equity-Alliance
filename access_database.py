import psycopg2
import sys
import os

DATABASE_URL = os.getenv('DATABASE_URL')
CONN = psycopg2.connect("dbname=oea user=postgres password=xxx")

# get list of programs for a student
# should be divided into three categories
# def get_student_programs():


# get complete list of programs
# divided into three(?) categories
def get_all_programs():
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
                    data_row['description'] = ro2[2]
                    data_row['initial_availability'] = row[3]

                return data

    except Exception as error:
            print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
            sys.exit(1)


# get complete list of students
# with some information??
# def get_all_students():

def main():
    programs = get_all_programs()
    print("Display programs list for admin: ")
    for program in programs:
        print("Program name:", program['program_name'])
        print("Program description:", program['description'])
        print("Program availability:" )

if __name__ == '__main__':
    main()
