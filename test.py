
# import os
import access_database
import modify_database
import display_database


def test_insert_students():
    # add Liz as student
    print('add student1 Liz')
    student_data = {
         'student_name': 'Liz Garcia',
         'student_email': 'lg6248@princeton.edu'
    }
    modify_database.insert_student(student_data)

    # add Annie as student
    print('add student2 Annie')
    student_data = {
         'student_name': 'Annie Liu',
         'student_email': 'an2334@princeton.edu'
    }
    modify_database.insert_student(student_data)

    # add Donna as student
    print('add student3 Donna')
    student_data = {
         'student_name': 'Donna Wang',
         'student_email': 'dw5609@princeton.edu'
    }
    modify_database.insert_student(student_data)


def main():
    # DATABASE_URL = os.getenv('DATABASE_URL')
    # print(DATABASE_URL)


    # #--------------test adding students -------------------------- #

    print("main: test adding students")
    print("current database: ")
    display_database.display_users_table()
    test_insert_students()
    display_database.display_users_table()






if __name__ == '__main__':
    main()
