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
    print("student program")
    username = auth.authenticate()
    authorize_student(username)

    program_id = flask.request.args.get('program_id')

    print(program_id)

    status, student_info = database.get_student_info(username)
    if not status: return error_response("student info")

    status, student_program_status = database.get_student_program_status(student_info['user_id'], program_id)
    if not status: return error_response("student program status")

    status, program_info = database.get_program_info(program_id)
    if not status: return error_response("program info")

    if student_program_status == 'enrolled':
        status, locked_index = database.get_locked_index(student_info['user_id'], program_id)
        if not status: return error_response("enrolled program locked index")
        print("locked_index",locked_index)
        html_code = flask.render_template('student_enrolled_program.html',
        program = program_info, student = student_info, locked_index = locked_index, username=username)
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

@app.route('/admin/students/add', methods=['POST'])
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

@app.route('/admin/admins/add', methods=['POST'])
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

    status, all_programs = database.get_all_programs()
    if status:
        html_code = flask.render_template('admin_programs.html',
                    programslist = all_programs, username=username)
    else:
        err_msg = "There was a server error while getting info about all programs. Please contact system administrator."
        html_code= flask.render_template('error.html',
                    err_msg = err_msg, username=username)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit', methods=['GET'])
def admin_edit_program():
    program_id = flask.request.args.get('program_id')
    #print('program id: ', program_id)

    status, program_info = database.get_program_info(program_id)

    if status:
        html_code = flask.render_template('admin_programdetails.html',
                            program = program_info,
                            moduleslist = program_info['modules'])
    else:
        err_msg = "There was a server error while getting program info. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/create', methods=['POST'])
def admin_create_program():
    program_data = {}
    program_data["program_name"] = flask.request.form['program_name']
    program_data["program_description"] = flask.request.form['program_description']
    program_data["program_availability"] = flask.request.form['program_availability']

    status, message = database.insert_program(program_data)

    if status:
        return flask.redirect(flask.url_for('admin_programs'))
    else:
        err_msg = "There was a server error while inserting program. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/delete', methods=['POST'])
def admin_delete_program():
    program_id = flask.request.form['program_id']

    status, message = database.delete_program(program_id)

    if status:
        return flask.redirect(flask.url_for('admin_programs'))
    else:
        err_msg = "There was a server error while deleting program. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit/name', methods=['POST'])
def admin_edit_program_name():

    program_id = flask.request.form['program_id']
    new_program_name = flask.request.form['new_program_name']

    status, message = database.update_program_name(program_id, new_program_name)

    if status:
        return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
    else:
        err_msg = "There was a server error while changing program name. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/edit/description', methods=['POST'])
def admin_edit_program_description():
    program_id = flask.request.form['program_id']
    new_program_description = flask.request.form['new_program_description']

    status, message = database.update_program_description(program_id, new_program_description)

    if status:
        return flask.redirect(flask.url_for('admin_edit_program', program_id = program_id))
    else:
        err_msg = "There was a server error while changing program description. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/edit/availability', methods=['POST'])
def admin_edit_program_availability():
    program_id = flask.request.form['program_id']
    new_program_availability = flask.request.form['new_program_availability']
    #print('Got new program avail! :', new_program_availability)

    status, message = database.update_program_availability(program_id, new_program_availability)
    #print('success of changing availability = ', success)

    if status: # if successfully changed program name
        return flask.redirect(flask.url_for('admin_edit_program', program_id = program_id))
    else:
        err_msg = "There was a server error while changing program availability. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response

# # MODULE FUNCTIONS STARTING HERE...

# display list of modules for specific program
@app.route('/admin/programs/modules', methods=['GET'])
def admin_program_modules():

    username = auth.authenticate()
    authorize_admin(username)

    program_id = flask.request.args.get('program_id')

    status, program_info = database.get_program_info(program_id)

    if status:
        html_code = flask.render_template('admin_edit_program.html',
                            program = program_info, username=username)
    else:
        err_msg = "There was a server error while getting program modules. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response

@app.route("/admin/programs/edit/add_module", methods=['POST'])
def admin_create_module():
    program_id = flask.request.form['program_id']

    module_data = {}
    module_data["program_id"] = program_id
    module_data["module_name"] = flask.request.form['module_name']
    module_data["content_link"] = flask.request.form['content_link']
    module_data["content_type"] = flask.request.form['content_type']

    status, module_id = database.insert_module(module_data)

    if status:
        return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
    else:
        err_msg = "There was a server error while inserting module. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/modules/delete', methods=['POST'])
def admin_delete_module():
    module_id = flask.request.form['module_id']
    program_id = flask.request.form['program_id']
    # program_id = flask.request.args.get('program_id')
    # print('program_id', program_id)

    status, message = database.delete_module(module_id)

    if status:
        return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
    else:
        err_msg = "There was a server error while deleting module. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/modules/edit/name', methods=['POST'])
def admin_edit_module_name():
    module_id = flask.request.form['module_id']
    program_id = flask.request.form['program_id']
    new_module_name = flask.request.form['new_module_name']

    status, message = database.update_module_name(module_id, new_module_name)

    # if successfully changed module name
    if status :
        return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
    else:
        err_msg = "There was a server error while changing module name. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response


#! edit content_type of module
@app.route('/admin/programs/modules/edit/content_type', methods= ['POST'])
def admin_edit_module_content_type():
    # module_id = flask.request.args.get('module_id')

    # program_id  = flask.request.args.get('program_id')
    # print('program_id = ', program_id)
    program_id = flask.request.form['program_id']
    module_id = flask.request.form['module_id']
    new_content_type = flask.request.form['new_content_type']

    status, message = database.update_module_content_type(module_id, new_content_type)
    if status:
        return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
    else:
        err_msg = "There was a server error while updating module content type. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response



@app.route('/admin/programs/modules/edit/link', methods=['GET','POST'])
def admin_edit_module_content_link():
    program_id = flask.request.form['program_id']
    module_id = flask.request.form['module_id']
    new_content_link = flask.request.form['new_content_link']

    status, message = database.update_module_content_link( module_id, new_content_link)
    if status:
        return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
    else:
        err_msg = "There was a server error while updating module link. Please contact system administrator."
        html_code = flask.render_template('error.html', err_msg = err_msg)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/edit/module_seq', methods=['POST'])
def edit_module_seq():

    program_id = flask.request.form['program_id']

    for name, val in flask.request.form.items():
        if name[0] != 'm': continue
        status, message = database.update_module_index(name, val)
        if not status:
            err_msg = "There was a server error while updating module link. Please contact system administrator."
            html_code = flask.render_template('error.html', err_msg = err_msg)
            response = flask.make_response(html_code)
            return response


    return flask.redirect(flask.url_for('admin_edit_program', program_id=program_id))
