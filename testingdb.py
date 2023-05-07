import database.py

# statement testing for database.py
def main():

    print('Inserting student!')

    # raise exception
    data = ''
    database.insert_student(data)

    # insert new student info
    student_data = {}
    student_data['student_email'] = 'Liz-Testing@gmail.com'
    student_data['student_name'] = 'Liz1-testing'
    database.insert_student(student_data)

    # exception email already in database
    student_data = {}
    student_data['student_email'] = 'Liz-Testing@gmail.com'
    student_data['student_name'] = 'Liz2-testing'
    database.insert_student(student_data)

# -------------------------------------------------------------------#
    print('Inserting admin1!')

    # raise exception
    data = ''
    database.insert_admin(data)

    # insert new admin info
    admin_data = {}
    admin_data['admin_email'] = 'Liz-Admin-Testing@gmail.com'
    admin_data['admin_name'] = 'Liz1-Admin-testing'
    database.insert_student(admin_data)

    # exception email already in database
    admin_data = {}
    admin_data['admin_email'] = 'Liz-Admin-Testing@gmail.com'
    admin_data['admin_name'] = 'Liz2-Admin-testing'
    database.insert_student(admin_data)

# -------------------------------------------------------------------#
    print('Deleting user!') # can delete student or admin

    # user id should not be none
    user_id = None
    database.delete_user(user_id)

    database.delete_user(6) # deleting Catherine

# -------------------------------------------------------------------#
    print("Insert program1!")

    # missing data program_name
    program1_data = {
                    "program_description": "Description",
                    "program_availability": "all"
                    }
    database.insert_program(program1_data)


    # create new program: Testing 101
    program1_data = {
                    "program_name": "Tree Ambassador 101",
                    "program_description": "Description",
                    "program_availability": "all"
                    }
    database.insert_program(program1_data)

# -------------------------------------------------------------------#
    print("Insert module")

    module_name = 'Liz statement testing'
    module_content_type = "assessment"
    module_content_link = 'statement testing link'

    module_data = {
        'program_id': 'p25', # insert module into created program
        'module_name': module_name,
        'content_type': module_content_type,
        'content_link': module_content_link,
    }

    database.insert_module(module_data)


# -------------------------------------------------------------------#

    print('Delete module')

    # invalid module_id
    id = None
    database.delete_module(id)

    id = ''
    database.delete_module(id)

    # should delete program successfully
    database.delete_module('p24')
# -------------------------------------------------------------------#

    print('Delete program1') # deletes program and associated module

    # invalid program_id
    id = None
    database.delete_program(id)

    id = ''
    database.delete_program(id)

    # should delete program successfully
    database.delete_program('p23')

# -------------------------------------------------------------------#

    print('Updating program name')

    # missing program id error
    program_id = ''
    new_program_name = 'hey'
    database.update_program_name(program_id, new_program_name)

    # missing program name error
    program_id = 'p24'
    new_program_name = None
    database.update_program_name(program_id, new_program_name)

    # should work
    program_id = 'p24'
    new_program_name = 'Liz doing statement testing'
    database.update_program_name(program_id, new_program_name)

# -------------------------------------------------------------------#
    print('Updating program description')

    # missing program id error
    program_id = ''
    new_program_desc = 'hello!'
    database.update_program_description(program_id, new_program_name)

    # missing program desc error
    program_id = 'p24'
    new_program_desc = None
    database.update_program_description(program_id, new_program_desc)

    # should work
    program_id = 'p24'
    new_program_desc = 'Liz doing statement testing'
    database.update_program_description(program_id, new_program_desc)

# -------------------------------------------------------------------#

    print('Updating program availability')

    # missing program id error
    program_id = ''
    new_program_avail = 'none'
    database.update_program_availability(program_id, new_program_avail)

    # missing program avail error
    program_id = 'p24'
    new_program_avail = None
    database.update_program_availability(program_id, new_program_avail)

    # should work
    program_id = 'p24'
    new_program_avail = 'Liz doing statement testing'
    database.update_program_availability(program_id, new_program_name)


# -------------------------------------------------------------------#
    print('Updating module name')

    # missing program id error
    program_id = ''
    module_id = 'm26'
    new_module_name = 'statement testing'
    database.update_module_name(program_id, module_id, new_module_name)

    # missing module id error
    program_id = 'p17'
    module_id = None
    new_module_name = 'statement testing'
    database.update_module_name(program_id, module_id, new_module_name)

    # missing new module name
    program_id = 'p24'
    module_id = 'm26'
    new_module_name = 'statement testing'
    database.update_module_name(program_id, module_id, new_module_name)

    # should work
    program_id = 'p24'
    module_id = 'm26'
    new_module_name = 'statement testing'
    database.update_module_name(program_id, module_id, new_module_name)

# -------------------------------------------------------------------#
    print('Update module content type')

    # invalid module id
    module_id = None
    new_content_type = "non-assessment"
    database.update_module_content_type(module_id, new_content_type)

    # missing content type
    module_id = 'm26'
    new_content_type = ''
    database.update_module_content_type(module_id, new_content_type)

    # should work
    module_id = 'm26'
    new_content_type = 'assessment'
    database.update_module_content_type(module_id, new_content_type)


# -------------------------------------------------------------------#
    print('Update module content link')

    # invalid module id
    module_id = None
    new_content_link = 'statement-testing.com'
    database.update_module_content_link(module_id, new_content_link)

    # misisng content link
    module_id = 'm26'
    new_content_link = ''
    database.update_module_content_link(module_id, new_content_link)

    # should work
    module_id = 'm26'
    new_content_link = 'Liz-statement.com'
    database.update_module_content_link(module_id, new_content_link)

# -------------------------------------------------------------------#

#! please do not use, should not be used on its own
## should only be used by edit_module_seq in oea


    # print('Update module index')

    # # invalid module_id
    # module_id =
    # new_module_index =
    # database.update_module_index(module_id, new_module_index)

    # # missing module index
    # module_id =
    # new_module_index =
    # database.update_module_index(module_id, new_module_index)

    # # should work
    # module_id =
    # new_module_index =
    # database.update_module_index(module_id, new_module_index)

# -------------------------------------------------------------------#
    print('update_program_status')

    # invalid student id
    student_id = None
    program_id = 'p17'
    new_program_status = 'none'
    database.update_program_status(student_id, program_id, new_program_status)


    # invalid program_id
    student_id = 6 # Catherine
    program_id = None
    new_program_status = 'none'
    database.update_program_status(student_id, program_id, new_program_status)

    # missing new program status
    student_id = 6
    program_id = 'p17'
    new_program_status = ''
    database.update_program_status(student_id, program_id, new_program_status)

    # should work
    student_id = 6
    program_id = 'p17'
    new_program_status = 'all'
    database.update_program_status(student_id, program_id, new_program_status)


# -------------------------------------------------------------------#
    print('Update assessment status')

    # invalid student id
    student_id = None
    module_id = 'm26'
    new_assessment_status = 'assessment'
    database.update_assessment_status(student_id, module_id, new_assessment_status)

    # invalid module id
    student_id = 6
    module_id = ''
    new_assessment_status = 'assessment'
    database.update_assessment_status(student_id, module_id, new_assessment_status)

    # missing new assessment status
    student_id = 6
    module_id = 'm26'
    new_assessment_status = ''
    database.update_assessment_status(student_id, module_id, new_assessment_status)

    # should work
    student_id = 6
    module_id = 'm26'
    new_assessment_status = 'asssessment'
    database.update_assessment_status(student_id, module_id, new_assessment_status)

# -------------------------------------------------------------------#
    print('Is admin authorized')


# -------------------------------------------------------------------#
    print('Is student authorized')

# -------------------------------------------------------------------#
    print('Get student info')

# -------------------------------------------------------------------#
    print('get all admins')


# -------------------------------------------------------------------#
    print('get all students')

# -------------------------------------------------------------------#
    print('get all programs')

# -------------------------------------------------------------------#
    print('get program info')


# -------------------------------------------------------------------#
    print('get module info')


# -------------------------------------------------------------------#
    print('get student program status')

# -------------------------------------------------------------------#
    print('get student enrolled program info')

# -------------------------------------------------------------------#
    print('get locked index')

# -------------------------------------------------------------------#
    print('get student program progress')


# -------------------------------------------------------------------#


if __name__ == '__main__':
    main()