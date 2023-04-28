import os
import flask
import database
import flask_talisman
import flask_wtf.csrf
import auth

# export APP_SECRET_KEY=xxx
# export GOOGLE_CLIENT_ID=658586292195-ct24h8p12spju4ib474k96g2g2pcalpi.apps.googleusercontent.com
# export GOOGLE_CLIENT_SECRET=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

app = flask.Flask(__name__, template_folder="./templates")

app.secret_key = os.environ['APP_SECRET_KEY']

# flask_wtf.csrf.CSRFProtect(app) #need to check out post form?? i.e. new admin
# flask_talisman.Talisman(app)


@app.route('/login', methods=['GET'])
def login():
    return auth.login()

@app.route('/login/callback', methods=['GET'])
def callback():
    return auth.callback()

@app.route('/logout', methods=['GET'])
def logout():
    return auth.logout()


@app.route('/', methods=["GET"])
@app.route('/index', methods=['GET'])
def index():
    html_code = flask.render_template('index.html')
    response = flask.make_response(html_code)
    return response


def authorize_admin(username):
    status, authorized = database.is_admin_authorized(username)
    if status:
        if not authorized:
            response = flask.make_response('You are not authorized to use this application.')
            flask.abort(response)
    else:
        response = flask.make_response('An error occured with the server. Try again later.')
        flask.abort(response)


def authorize_student(username):
    status, authorized = database.is_student_authorized(username)
    if status:
        if not authorized:
            response = flask.make_response('You are not authorized to use this application.')
            flask.abort(response)
    else:
        response = flask.make_response('An error occured with the server. Try again later.')
        flask.abort(response)

def error_response(err_location):
    err_msg = "There was a server error while getting " + err_location + ". Please try again later."
    html_code = flask.render_template('error.html', err_msg = err_msg)
    response = flask.make_response(html_code)
    return response

@app.route('/admin', methods=['GET'])
def admin_interface():

    username = auth.authenticate()
    authorize_admin(username)

    html_code = flask.render_template('admin_interface.html')
    response = flask.make_response(html_code)
    return response

@app.route('/student', methods=['GET'])
def student_interface():
    username = auth.authenticate()
    authorize_student(username)

    status, student_info = database.get_student_info(username)
    if status:
        html_code = flask.render_template('student_interface.html',
                    student = student_info, username=username)
    else:
        err_msg = "There was a server error while getting student programs. Please try again later."
        html_code = flask.render_template('error.html', err_msg = err_msg)
    response = flask.make_response(html_code)
    return response

@app.route('/student/program', methods=['GET'])
def student_program():
    username = auth.authenticate()
    authorize_student(username)

    program_id = flask.request.args.get('program_id')

    status, student_info = database.get_student_info(username)
    if not status: return error_response("student info")

    status, student_program_status = database.get_student_program_status(student_info['user_id'], program_id)
    if not status: return error_response("student program status")

    status, program_info = database.get_program_info(program_id)
    if not status: return error_response("program info")


    if student_program_status == 'enrolled':
        status, locked_index = database.get_locked_index(student_info['user_id'], program_id)
        if not status: return error_response("enrolled program locked index")
        html_code = flask.render_template('student_enrolled_program.html',
                    program = program_info, student = student_info, username=username, locked_index=locked_index)
    elif student_program_status == 'available':
        html_code = flask.render_template('student_available_program.html',
                    program = program_info, student=student_info, username=username)
    elif student_program_status == 'locked':
        html_code = flask.render_template('student_locked_program.html',
                program = program_info, student=student_info, username=username)

    response = flask.make_response(html_code)
    return response

@app.route('/student/program/enroll_program', methods=['POST'])
def student_enroll_program():
    student_id = flask.request.form['student_id']
    program_id = flask.request.form['program_id']
    status, message = database.update_program_status(student_id, program_id, "enrolled")

    if status:
        return flask.redirect(flask.url_for('student_program', program_id=program_id))
    else:
        err_msg = "There was a server error while trying to enroll in the program. Please contact the system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
        response = flask.make_response(html_code)
        return response


@app.route('/student/program/module', methods=['GET'])
def student_program_module():

    username = auth.authenticate()
    authorize_student(username)

    module_id = flask.request.args.get('module_id')

    status, student_info = database.get_student_info(username)
    if not status: return error_response("student info")

    status, module_info = database.get_module_info(module_id)
    if not status: return error_response("module info")

    status, program_info = database.get_program_info(module_info['program_id'])
    if not status: return error_response("program info")

    status, program_status = database.get_student_program_status(student_info['user_id'], program_info['program_id'])
    if not status: return error_response("student program status")

    status, locked_index = database.get_locked_index(student_info['user_id'], program_info['program_id'])
    if not status: return error_response("program locked index")

    if program_status != "enrolled" or module_info['module_index'] > locked_index:
        err_msg = "You cannot access this module. Either you're not enrolled or prior assessments must be complete and approved."
        html_code = flask.render_template('error.html', err_msg = err_msg)
    else:
        html_code = flask.render_template('student_program_module.html',
                            module = module_info, program=program_info, student=student_info, locked_index = locked_index, username=username)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/students', methods=['GET'])
def admin_students():

    username = auth.authenticate()
    authorize_admin(username)

    status, students = database.get_all_students()

    if status:
        html_code = flask.render_template('admin_students.html', students=students)
    else:
        err_msg = "There was a server error while getting all students.Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/students/add_student', methods=['POST'])
def add_student():

    user_info = {}
    # user_info["user_id"] = modify_database.create_program_id()
    user_info["student_name"] = flask.request.form['student_name']
    user_info["student_email"] = flask.request.form['student_email']
    status, message = database.insert_student(user_info)

    if status:
        return flask.redirect(flask.url_for('admin_students'))
    else:
        err_msg = "There was a server error while adding student. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
        response = flask.make_response(html_code)
        return response


@app.route('/admin/students/delete', methods=['POST'])
def delete_student():
    student_id = flask.request.form['student_id']
    status, message = database.delete_user(student_id)

    if status:
        return flask.redirect(flask.url_for('admin_students'))
    else:
        err_msg = "There was a server error while deleting admin. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
        response = flask.make_response(html_code)
        return response




@app.route('/admin/students/student_details', methods=['GET'])
def admin_student_details():

    username = auth.authenticate()
    authorize_admin(username)

    student_email = flask.request.args.get('student_email')
    #print(student_email)

    status, student_info = database.get_student_info(student_email)
    #print("student_info", student_info)
    if not status: error_response("student information")

    status, enrolled_programs = database.get_student_enrolled_program_info(student_info['user_id'])
    if not status: error_response("student enrolled program information")

    #print("Student Interface: displaying programs list")
    html_code = flask.render_template('admin_studentdetails.html',
                student = student_info,
                enrolled_programs = enrolled_programs, username=username)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/students/student_details/update_program_status', methods=['POST'])
def update_program_status():
    student_id = flask.request.form['student_id']
    student_email = flask.request.form['student_email']
    program_id = flask.request.form['program_id']
    program_status = flask.request.form['user_program_status']
    status, msg = database.update_program_status(student_id, program_id, program_status)

    if status:
        return flask.redirect(flask.url_for('admin_student_details', student_email=student_email))
    else:
        err_msg = "There was a server error while updating student program status. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
        response = flask.make_response(html_code)
        return response

@app.route('/admin/students/student_details/update_module_status', methods=['POST'])
def update_module_status():
    student_email = flask.request.form['student_email']
    student_id = flask.request.form['student_id']
    assessment_id = flask.request.form['assessment_id']
    assessment_status = flask.request.form['user_assessment_status']

    status, msg = database.update_assessment_status(student_id, assessment_id, assessment_status)

    if status:
        return flask.redirect(flask.url_for('admin_student_details', student_email=student_email))
    else:
        err_msg = "There was a server error while updating student assessment status. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
        response = flask.make_response(html_code)
        return response

@app.route('/admin/admins', methods=['GET'])
def admin_admins():

    username = auth.authenticate()
    authorize_admin(username)

    status, admins = database.get_all_admins()

    if status:
        html_code = flask.render_template('admin_admins.html', admins=admins)
    else:
        err_msg = "There was a server error while getting all students. Please try again later."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/admins/add_admin', methods=['POST'])
def add_admin():

    user_info = {}
    user_info["admin_name"] = flask.request.form['admin_name']
    user_info["admin_email"] = flask.request.form['admin_email']
    success, message = database.insert_admin(user_info)

    if success:
        return flask.redirect(flask.url_for('admin_admins'))
    else:
        err_msg = "There was a server error while adding admin. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
        response = flask.make_response(html_code)
        return response

@app.route('/admin/admins/delete', methods=['POST'])
def delete_admin():
    user_id = flask.request.form['user_id']
    success, message = database.delete_user(user_id)

    if success:
        return flask.redirect(flask.url_for('admin_admins'))
    else:
        err_msg = "There was a server error while deleting admin. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
        response = flask.make_response(html_code)
        return response


@app.route('/admin/programs', methods=['GET'])
def admin_programs():

    username = auth.authenticate()
    authorize_admin(username)

    status, data = database.get_all_programs()
    if status:
        print("Admin Interface: displaying programs list")
        html_code = flask.render_template('admin_programs.html',
                    programslist = data, username=username)
    else:
        print("Error: " + data)
        html_code= flask.render_template('error.html',
                    err_msg = data, username=username)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit', methods=['GET'])
def admin_edit_program():
    program_id = flask.request.args.get('program_id')
    print('program id: ', program_id)

    status, program_info = database.get_program_info(program_id)

    if status:
        html_code = flask.render_template('admin_programdetails.html',
                            pgm_data = program_info,
                            moduleslist = program_info['modules'])
    else:
        err_msg = "There was a server error while getting program info. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response

# return flask.redirect(flask.url_for('admin_programs'))

@app.route('/admin/programs/create_program', methods=['GET','POST'])
def admin_create_program():
    print("creating program...")
    if flask.request.method == 'POST':
        pgm_params = {}
        pgm_params["program_name"] = flask.request.form['pgm_name']
        # create program_id
        is_duplicate = database.is_program_name_duplicate(pgm_params["program_name"])
        print("is pgm name duplicate?", is_duplicate)

        # status, pgm_params["program_id"] = database.create_program_id()
        # print('did creation of program id work? ', status)

        pgm_params["program_description"] = flask.request.form['pgm_descrip']
        pgm_params["program_availability"] = flask.request.form['pgm_avail']

        success, program_id = database.insert_program(pgm_params)
        print('success of insert program = ', success)

        if success and not is_duplicate:
            print("new program inserted = ", program_id)
            return flask.redirect(flask.url_for('admin_programs'))
        elif is_duplicate:
            data = """ Duplicate program name. Please click the back button \
                on the top left corner and input a unique program name."""
            html_code = flask.render_template('error.html',
                                err_msg = data)
        else:
            data = """ There was a server error while inserting program.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/delete/program', methods=['POST'])
def delete_program():
    program_id = flask.request.args.get('program_id')

    # if not modify_database.existingProgramID(program_id):
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    print('program_id = ', program_id)
    success, message = database.delete_program(program_id)
    print("success in deleting program?", success)

    if success:
        print("Admin Interface: displaying programs list")
        return flask.redirect(flask.url_for('admin_programs'))
    else:
        html_code = flask.render_template('error.html',
                            err_msg = message)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit/name', methods=['GET', 'POST'])
def edit_program_name():

    pgm_id = flask.request.args.get('program_id')
    print('program id: ', pgm_id)

    # if not modify_database.existingProgramID(pgm_id):
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    if flask.request.method == 'POST':
        # get new name from text input field
        new_program_name = flask.request.form['new_program_name']
        print('Got new program name! :', new_program_name)

        is_duplicate = database.is_program_name_duplicate(new_program_name)
        print("is program name duplicate? = ", is_duplicate)

        # if modify_database.existingProgramID(pgm_id):
        success, message = database.update_program_name(pgm_id, new_program_name)
        print('success of changing name = ', success)

        if success and not is_duplicate: # if successfully changed program name
            return flask.redirect(flask.url_for('admin_programs'))
        elif is_duplicate:
            err_msg = "Duplicate program name. Please click the back button \
                on the top left corner and input a unique program name."
            html_code = flask.render_template('error.html',
                                err_msg = err_msg)
        else:
            err_msg = "There was a server error while changing program name. \
            Please contact system administrator."
            html_code = flask.render_template('error.html',
                                err_msg = err_msg)


    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/edit/description', methods=['GET', 'POST'])
def edit_program_desc():
    pgm_id = flask.request.args.get('program_id')
    print('program id: ', pgm_id)

    # if not database.existingProgramID(pgm_id):
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    if flask.request.method == 'POST':
        # get new desc from text input field
        new_program_desc = flask.request.form['new_pgm_desc']
        print('Got new program desc! :', new_program_desc)

        # if database.existingProgramID(pgm_id):
        success, message = database.update_program_description(pgm_id, new_program_desc)
        print('success of changing description = ', success)

        if success:
            return flask.redirect(flask.url_for('admin_programs'))
        else:
            data = """ There was a server error while changing program description.
            Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/edit/availability', methods=['GET', 'POST'])
def edit_program_avail():
    pgm_id = flask.request.args.get('program_id')
    print('program id: ', pgm_id)

    # if not database.existingProgramID(pgm_id):
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    if flask.request.method == 'POST':
        # get new desc from text input field
        new_program_avail = flask.request.form['new_pgm_avail']
        print('Got new program avail! :', new_program_avail)

        success, message = database.update_program_availability(pgm_id, new_program_avail)
        print('success of changing availability = ', success)

        if success: # if successfully changed program name
            return flask.redirect(flask.url_for('admin_programs'))
        else:
            data = """ There was a server error while changing program availability.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response

# # MODULE FUNCTIONS STARTING HERE...

# display list of modules for specific program
@app.route('/admin/programs/modules', methods=['GET'])
def admin_program_modules():

    username = auth.authenticate()
    authorize_admin(username)

    program_id = flask.request.args.get('program_id')
    print('modules page program id = ', program_id)

    # if not modify_database.existingProgramID(program_id):
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    status, program_info = database.get_program_info(program_id)
    print('status of getting program info = ', status)

    if status:
        html_code = flask.render_template('admin_edit_program.html',
                            program = program_info, username=username)
    else:
        err_msg = "There was a server error while getting program modules. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response

@app.route("/admin/programs/edit/add_module", methods=['GET', 'POST'])
def admin_create_module():
    program_id = flask.request.args.get('program_id')
    print('program_id in create module function = ', program_id)

    # if not database.existingProgramID(program_id):
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    if flask.request.method == 'POST':
        # modules_params
        md_params = {}

        md_params["program_id"] = program_id
        md_params["module_name"] = flask.request.form['module_name']
        md_params["content_link"] = flask.request.form['content_link']
        md_params["content_type"] = flask.request.form['content_type']

        is_duplicate = database.is_module_name_duplicate(md_params['module_name'])
        print('is module name duplicate = ', is_duplicate)

        success, module_id = database.insert_module(md_params)
        md_params["module_id"] = module_id

        print('success of inserting module = ', success)

        if success and not is_duplicate:
            return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
        elif is_duplicate:
            message = """ Duplicate module name. Please click the back button
            on the top left corner and input a unique module name."""
            html_code = flask.render_template('error.html', err_msg = message)
        else:
            data = """ There was a server error while inserting module.
            Please contact system administrator."""
            html_code = flask.render_template('error.html', err_msg = data)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/modules/delete', methods=['POST'])
def delete_module():
    module_id = flask.request.args.get('module_id')
    print('module_id', module_id)

    # if not database.existingModuleID(module_id):
    #     message = "Invalid module id. Please contact system administrator."
    #     return errorResponse(message)

    program_id = flask.request.args.get('program_id')
    print('program_id', program_id)

    # if not database.existingProgramID(program_id):
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    success, message = database.delete_module(module_id)
    print("deleting module success = ", success)

    if success:
        return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
    else:
        data = """ There was a server error while deleting module.
        Please contact system administrator."""
        html_code = flask.render_template('error.html',
                            err_msg = data)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/modules/edit/name', methods=['GET', 'POST'])
def edit_module_name():
    module_id = flask.request.args.get('module_id')

    # if not modify_database.existingModuleID(module_id):
    #     print('inside check function of nonexistant module id')
    #     message = "Invalid module id. Please contact system administrator."
    #     return errorResponse(message)

    # elif module_id == "":
    #     print("module_id is none")
    # print('GET get MODULE_ID', module_id)
    program_id = flask.request.args.get('program_id')
    # print('program_id = ', program_id)

    # if not modify_database.existingProgramID(program_id):
    #         print('inside invalid program id check')
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    if flask.request.method == 'POST':
        new_module_name = flask.request.form['new_module_name']
        print('post get new module name: ', new_module_name)

        is_duplicate = database.is_module_name_duplicate(new_module_name)

        success, message = database.update_module_name(module_id, new_module_name )

        if success and not is_duplicate: # if successfully changed module name
            return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
        elif is_duplicate:
            message = """ Duplicate module name. Please click the back button
            on the top left corner and input a unique module name."""
            html_code = flask.render_template('error.html', err_msg = message)
        else:
            data = """ There was a server error while changing module name.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response


#! edit content_type of module
@app.route('/admin/programs/modules/edit/content_type', methods= ['POST'])
def edit_module_content_type():
    # module_id = flask.request.args.get('module_id')

    # program_id  = flask.request.args.get('program_id')
    # print('program_id = ', program_id)

    if flask.request.method == 'POST':
        new_type = flask.request.form['new_content_type']
        print('new content type = ', new_type)

        program_id = flask.request.form['program_id']
        print('program_id ', program_id)

        module_id = flask.request.form['module_id']
        print('module_id ', module_id)

        success, message = database.update_module_content_type(module_id, new_type)
        print('success of updating module content type = ', success)
        if success:
            return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
        else:
            err_msg = "There was a server error while updating module content type. Please contact system administrator."
            html_code = flask.render_template('error.html',
                                err_msg = err_msg)

    response = flask.make_response(html_code)
    return response



@app.route('/admin/programs/modules/edit/link', methods=['GET','POST'])
def edit_module_link():
    print('entering editing link function...')

    # if not modify_database.existingModuleID(module_id):
    #     message = "Invalid module id. Please contact system administrator."
    #     return errorResponse(message)

    # if not modify_database.existingProgramID(program_id):
    #         message = "Invalid program id. Please contact system administrator."
    #         return errorResponse(message)

    if flask.request.method == 'POST':
        program_id = flask.request.form['program_id']
        print('program_id ', program_id)

        module_id = flask.request.form['module_id']
        print('module_id ', module_id)

        new_module_link = flask.request.form['new_module_link']
        print('new_module_link = ', new_module_link)

        success, message = database.update_module_content_link( module_id, new_module_link)
        print('success of updating module link = ', success)
        if success:
            return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
        else:
            data = """ There was a server error while updating module link.
            Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/edit/module_seq', methods=['POST'])
def edit_module_seq():

    program_id = flask.request.form['program_id']

    for name, val in flask.request.form.items():
        if name[0] != 'm': continue
        status, message = database.update_module_index(name, val)
        if not status: return errorResponse("updating module index")


    return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
