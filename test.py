
# import os
import access_database
import modify_database
import display_database


def test_insert_students():
    print("current users table: ")
    display_database.display_users_table()


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

    print("updated students table:")
    display_database.display_users_table()

def test_insert_pgm1():
    print("current programs table: ")
    display_database.display_programs_table()

    # create new program: Tree Ambassador 101
    print("program id: create program id")
    program1_id = modify_database.create_program_id()
    print("program1 id:", program1_id)
    program1_data = {"program_id": program1_id,
                    "program_name": "Tree Ambassador 101",
                    "description": "Description",
                    "program_availability": "all"
                    }
    print('data: ', program1_data)
    # program1_data = [program1_id, "Tree Ambassador 101", "Description", "all"]
    modify_database.insert_program(program1_data)

    print("updated programs table:")
    display_database.display_programs_table()

    print("-----------------")

    print("inserting modules")

    print("current data tables: ")
    display_database.main()

    # insert module 1 of tree ambassador 101
    module1_id = modify_database.create_module_id()
    print("module1 id: ", module1_id)
    module1_name = 'M1 Instructions'
    module1_content_type = "text"
    module1_content_link = 'https://docs.google.com/document/d/1PP-GiTqVcvJYpqVUxQ_bXSsru6H200l39RovL0AhYgw/edit?usp=sharing'
    module1_index = 1 #idea: need a function to get index
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

    modify_database.insert_module(module1_data)
    print("main: insert module1")


    # insert module 2 of tree ambassador 101
    module2_id = modify_database.create_module_id()
    print('module2 id: ', module2_id)
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


    modify_database.insert_module(module2_data)
    print("main: insert module2")

    print("updated data table:")
    display_database.main()

def test_insert_pgm2():

    # create locked program
    program2_id = modify_database.create_program_id()
    program2_data = {
        "program_id": program2_id,
        "program_name": "Test - LOCKED PROGRAM",
        "description": "Description",
        "program_availability": "none"
    }
    # program2_data = [program2_id, "LOCKED PROGRAM", "Description", "NONE"]
    modify_database.insert_program(program2_data)
    print("main: program2 inserted")

    # create random module in program2
    module3_id = modify_database.create_module_id()
    module3_name = 'test module' # module 1 not a typo
    module3_content_type = "content type"
    module3_content_link = 'content link'
    module3_index = 1 # need a function to get index

    # module2_data = [module2_id, program1_id, module2_name, module2_content_type, module2_content_link, module2_index]

    module3_data = {
        'module_id' : module3_id,
        'program_id': program2_id,
        'module_name': module3_name,
        'content_type': module3_content_type,
        'content_link': module3_content_link,
        'module_index': module3_index
    }


    modify_database.insert_module(module3_data)
    print("main: insert module3")

    print("updated data table:")
    display_database.main()

def test_update_assess_status():
    print("current users table:")
    display_database.display_users_table()

    Liz_id = modify_database.get_student_id('lg6248@princeton.edu')
    print(Liz_id)
    #print(program1_id)
    modify_database.update_assessment_status(Liz_id, 'M2', 1)

    print("updated users table:")
    display_database.display_users_table()

def test_update_pgm_status():
    print("current data tables:")
    display_database.main()

    Liz_id = modify_database.get_student_id('lg6248@princeton.edu')
    print(Liz_id)
    #print(program1_id)
    modify_database.update_program_status(Liz_id, 'P1', 'locked')

    print("updated data tables:")
    display_database.main()


def main():
    # DATABASE_URL = os.getenv('DATABASE_URL')
    # print(DATABASE_URL)


    # #--------------test adding students -------------------------- #

    print("main: test adding students")
    test_insert_students()


    # # ------------creating test program 1 and modules ------------ #
    print("main: test insert pgm1")
    test_insert_pgm1()


    # # -------creating test locked program 2 and modules ---------- #
    # print("main: test insert locked program")
    # test_insert_pgm2()

    # ---------- test update pgm status ------


    print("main: test update pgm status")
    test_update_pgm_status()








if __name__ == '__main__':
    main()
