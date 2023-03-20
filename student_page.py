# Implement a function to access the database and obtain a list of
# students which will be displayed on the student page of the admin UI.

import os
import sys
import psycopg2

DATABASE_URL = os.getenv('DATABASE_URL')
def students_info():
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
            # query the students table. Make dictionaries as follows:
            # 1- key = student id, value = student name
            # 2- key = student id, value = student email
            # 3- key = student id, value = enrollment status
            # 4- key = student id, value = assessment completition status
                statement = """ SELECT student_id, student_name, student_email FROM students"""
                cursor.execute(statement)
#! need to modify based on program and quiz...
                data = cursor.fetchall()

            # table will be a list containing dictionaries,
            # where each dictionary contains the student_id,
            # name and email of a particular student.
            # Ex: [dict1, dict2...]
            # dict1 {id, name, email} --> first element
            # of table (type list)
                table = []

                index = 0
                for row in data:
                    myDict = {
                        'student_id' : row[0],
                        'student_name' : row[1],
                        'student_email': row[2],
                    }
                    table.append(myDict)


    except Exception as error:
        print(sys.argv[0] + ': ' + str(error), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    students_info()
