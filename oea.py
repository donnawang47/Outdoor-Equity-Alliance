import os
import flask
from flask import request
import access_database
import modify_database
import display_database
# import flask_wtf.csrf
import flask_talisman
import auth

# export APP_SECRET_KEY=xxx
# export GOOGLE_CLIENT_ID=658586292195-ct24h8p12spju4ib474k96g2g2pcalpi.apps.googleusercontent.com
# export GOOGLE_CLIENT_SECRET=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

app = flask.Flask(__name__, template_folder=".")

app.secret_key = os.environ['APP_SECRET_KEY']
#flask_wtf.csrf.CSRFProtect(app) -- need to check out post form?? i.e. new admin
#flask_talisman.Talisman(app)


#routes for authetication
@app.route('/login', methods=['GET'])
def login():
    return auth.login()

@app.route('/login/callback', methods=['GET'])
def callback():
    return auth.callback()

@app.route('/logoutapp', methods=['GET'])
def logoutapp():
    return auth.logoutapp()

@app.route('/logoutgoogle', methods=['GET'])
def logoutgoogle():
    return auth.logoutgoogle()

def authorize_admin(username):

    #74: def is_authorized(username):
    #in database.py file
# 75:
# 76: with sqlalchemy.orm.Session(_engine) as session:
# 77: query = session.query(AuthorizedUser).filter(AuthorizedUser.username==username)
# 79: try:
# 80: query.one()
# 81: return True
# 82: except sqlalchemy.exc.NoResultFound:
# 83: return False
    status, authorized = access_database.is_admin_authorized(username)
    if status:
        if not authorized:
            html_code = 'You are not authorized to use this application.'
            response = flask.make_response(html_code)
            flask.abort(response)

def authorize_student(username):
    status, authorized = access_database.is_student_authorized(username)
    if status:
        if not authorized:
            html_code = 'You are not authorized to use this application.'
            response = flask.make_response(html_code)
            flask.abort(response)

# temporary main page
# not sure what it should be
@app.route('/', methods=["GET"])
@app.route('/index', methods=['GET'])
def index():

    username = auth.authenticate()
    authorize_admin(username)

    html_code = flask.render_template('index.html')
    response = flask.make_response(html_code)
    return response


# admin interface main page
# menu for programs page and students page
@app.route('/admin', methods=['GET'])
def admin_interface():

    username = auth.authenticate()
    authorize_admin(username)

    html_code = flask.render_template('admin_interface.html')
    response = flask.make_response(html_code)
    return response

# admin
@app.route('/admin/admins', methods=['GET'])
def admin_admins():
    #status, students = access_database.get_all_students()

    username = auth.authenticate()
    authorize_admin(username)

    status, admins = access_database.get_all_admins()

    if status:
        html_code = flask.render_template('admin_admins.html', admins=admins)
    else:
        data = """ There was a server error while getting all students.
        Please contact system administrator."""
        html_code = flask.render_template('error.html', err_msg = data)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/students', methods=['GET'])
def admin_students():

    username = auth.authenticate()
    authorize_admin(username)

    status, students = access_database.get_all_students()

    if status:
        html_code = flask.render_template('admin_students.html', students=students, username=username)
    else:
        data = """ There was a server error while getting all students.
        Please contact system administrator."""
        html_code = flask.render_template('error.html', err_msg = data)
    response = flask.make_response(html_code)
    return response

# display error html page
def errorResponse(message):
    print('REACHED ERROR RESPONSE FUNCTION' + '\n')
    html_code = flask.render_template('error.html', err_msg = message)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/students/studentdetails', methods=['GET','POST'])
def admin_studentdetails():

    username = auth.authenticate()
    authorize_admin(username)

    studentid = flask.request.args.get('studentid')
    print("studentid", studentid)

    # updating status
    if flask.request.args.get('updateStatus') == 'true':
        id = flask.request.args.get('id')
        category = flask.request.args.get('category')
        print("id", id)
        if flask.request.method == 'POST':
            if category == 'pgm':
                pgm_progress = flask.request.form['pgm_progress']
                print("pgm_progress", pgm_progress)
                status, msg = modify_database.update_program_status(studentid, id, pgm_progress)
                if not status:
                    data = """ There was a server error while updating
                    program status. Please contact system administrator."""
                    return errorResponse(data)

                print("oea updating program status:", msg)
            elif category == 'module':
                mod_status = flask.request.form['mod_status']
                status, msg = modify_database.update_assessment_status(studentid, id, mod_status)
                if not status:
                    data = """ There was a server error while updating
                    assessment status. Please contact system administrator."""
                    return errorResponse(data)
                print("oea updating module status:", msg)

    #status, student_programs = access_database.get_student_programs(studentid)
    status2, student_info = access_database.get_student_info(studentid)

    # if not status:
    #     data = """There was a server error while getting student programs.
    #     Please contact system administrator."""
    #     errorResponse(data)
    if not status2:
        data = """ There was a server error while getting student information.
        Please contact system administrator."""
        return errorResponse(data)

    print("oea: get student programs done")
    # can only get student progress on enrolled programs?
    # need to change to enrolled
    enrolled = student_info['Enrolled Programs'] # program ids
    print(enrolled)
    enrolled_pgms = {} # pgm_id : status
    for pgm in enrolled:
        program_id = pgm['program_id']

        if not modify_database.existingProgramID(program_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

        success, pgm_progress = access_database.get_student_program_progress(studentid, program_id)

        if not success:
            data = """ There was a server error while getting student program progress.
            Please contact system administrator."""
            return errorResponse(data)

        print("pgm_progress" + pgm_progress)
        pgm['pgm_progress'] = pgm_progress
        #status, data = access_database.get_program_details(pgm_id)
        # if not status:
        #     data = """ There was a server error while getting program details.
        #     Please contact system administrator."""
        #     errorResponse(data)

        assessments = []
        # finds assessment modules for each pgm
        for mod in pgm['modules']:
            print(mod)
            if mod['content_type'] == 'assessment':
                module_id = mod['module_id']
                if not modify_database.existingModuleID(module_id):
                    message = "Invalid module id. Please contact system administrator."
                    return errorResponse(message)
                elif student_info[module_id] == 1:
                    mod['module_progress'] = "complete"
                else:
                    mod['module_progress'] = "incomplete"
                print("ASSESSMENT INFO:", mod)
                assessments.append(mod)
                #assessments.append((mod['module_id'], student_info[mod['module_id']]))
        pgm['assessments'] = assessments
        #enrolled_pgms[pgm_id] = pgm

    #print("oea.py, enrolled_pgms:", enrolled_pgms)

    print("Student Interface: displaying programs list")
    html_code = flask.render_template('admin_studentdetails.html',
                studentid = studentid,
                student_info = student_info,
                enrolled_pgms = student_info['Enrolled Programs'])
    response = flask.make_response(html_code)
    return response



@app.route('/admin/admins/new_admin', methods=['GET','POST'])
def admin_new_admin():
    if flask.request.method == 'POST':

        user_status = "admin"

        user_info = {}
        # user_info["user_id"] = modify_database.create_program_id()
        user_info["admin_name"] = flask.request.form['admin_name']
        user_info["admin_email"] = flask.request.form['admin_email']
        success, message = modify_database.insert_admin(user_info)


        if success:
            print("admin inserted")
            status, students = access_database.get_all_students()
            status, data = access_database.get_all_admins()
            if status:
                print("Admin Interface: displaying user list")
                html_code = flask.render_template('admin_admins.html',admins=data)
            else:
                print("Error: " + data)
                html_code= flask.render_template('error.html',
                            err_msg = data)
        else:
            html_code = flask.render_template('error.html',
                                err_msg = "A server error occurred while inserting program.")

    response = flask.make_response(html_code)
    return response

@app.route('/admin/students/new_student', methods=['GET','POST'])
def admin_new_user():
    if flask.request.method == 'POST':

        user_status = "student"

        user_info = {}
        # user_info["user_id"] = modify_database.create_program_id()
        user_info["student_name"] = flask.request.form['student_name']
        user_info["student_email"] = flask.request.form['student_email']
        success, message = modify_database.insert_student(user_info)

        if success:
            print("student inserted")
            status, data = access_database.get_all_students()
            if status:
                print("Admin Interface: displaying user list")
                html_code = flask.render_template('admin_students.html', students=data)
            else:
                print("Error: " + data)
                html_code= flask.render_template('error.html',
                            err_msg = data)
        else:
            html_code = flask.render_template('error.html',
                                err_msg = "A server error occurred while inserting program.")

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs', methods=['GET'])
def admin_programs():

    username = auth.authenticate()
    authorize_admin(username)

    status, data = access_database.get_programslist()
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

@app.route('/admin/programs/create_program', methods=['GET','POST'])
def admin_create_program():
    print("creating program...")
    if flask.request.method == 'POST':
        pgm_params = {}
        pgm_params["program_name"] = flask.request.form['pgm_name']
        # create program_id
        isDuplicate = modify_database.isProgramNameDuplicate(pgm_params["program_name"])  #todo: duplicate
        print("is pgm name duplicate?", isDuplicate)
        status, pgm_params["program_id"] = modify_database.create_program_id()
        pgm_params["description"] = flask.request.form['pgm_descrip']
        pgm_params["program_availability"] = flask.request.form['pgm_avail']

        success, message = modify_database.insert_program(pgm_params)
        print("done modifying:", message)
        #status, programslist = access_database.get_programslist()

        if success and status and not isDuplicate:
            print("new program inserted")
            success, data = access_database.get_programslist()
            if success:
                print("Admin Interface: displaying programs list")
                html_code = flask.render_template('admin_programs.html',
                            programslist = data)
            else:
                print("Error: " + data)
                html_code= flask.render_template('error.html',
                            err_msg = data)
        elif(isDuplicate):
            print("duplicate name") #! This should display alert message, not send error page. Give user another try.
        elif(not status):
            data = """ There was a server error while creating program id.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)
        elif(not success):
            data = """ There was a server error while inserting program.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)


    response = flask.make_response(html_code)
    return response

@app.route("/admin/programs/edit/add_module", methods=['GET', 'POST'])
def admin_create_module():
    program_id = flask.request.args.get('program_id')

    if not modify_database.existingProgramID(program_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    elif flask.request.method == 'POST':
        # modules_params
        md_params = {}
        status, md_params["module_id"] = modify_database.create_module_id()

        if not status:
            data = """ There was a server error while creating module id.
            Please contact system administrator."""
            html_code = flask.render_template('error.html', err_msg = data)
            response = flask.make_response(html_code)
            return response

        md_params["program_id"] = program_id
        md_params["module_name"] = flask.request.form['module_name']
        md_params["content_link"] = flask.request.form['content_link']
        md_params["content_type"] = flask.request.form['content_type']
         # md_params["module_index"] = flask.request.form['index']

        success, md_params["module_index"] = \
                                modify_database.create_module_index()
        if not success:
            message = "A server error occurred while creating index for new module. Please contact system administrator."
            return errorResponse(message)

        success, msg = modify_database.insert_module(md_params)
        if success:
            print(msg)
            success, data = access_database.get_program_details(program_id)
            if success: # return back to programs page
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                html_code = flask.render_template('error.html',
                                err_msg = data)

        else:
            data = """ There was a server error while inserting module.
        Please contact system administrator."""
            html_code = flask.render_template('error.html', err_msg = data)
    # else:
    #     program_name = flask.request.args.get('program_name')
    #     html_code = flask.render_template('admin_create_module.html', program_name)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit', methods=['GET', 'POST'])
def admin_edit_program():
    pgm_id = flask.request.args.get('program_id')
    print('program id: ', id)

    if not modify_database.existingProgramID(pgm_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    success, data = access_database.get_program_details(pgm_id)
    if success:
        print("data retrieved:",data)
        html_code = flask.render_template('admin_programdetails.html',
                            pgm_data = data,
                            moduleslist = data['modules'])
    else:
        data = """ There was a server error while getting program details.
        Please contact system administrator."""
        html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response

#TODO: ASK why we can reference html_code outside of scope?
@app.route('/admin/programs/edit/name', methods=['GET', 'POST'])
def edit_program_name():

    pgm_id = flask.request.args.get('program_id')
    print('program id: ', id)

    if not modify_database.existingProgramID(pgm_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    elif flask.request.method == 'POST':
        # get new name from text input field
        new_program_name = flask.request.form['new_program_name']
        print('Got new program name! :', new_program_name)

        if modify_database.existingProgramID(pgm_id):
            success, message = modify_database.change_program_name(pgm_id, new_program_name)
        else:
            data = """ Invalid program id.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

        if success: # if successfully changed program name
            status, data = access_database.get_program_details(pgm_id)
            if status:
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                data = """ There was a server error while getting program details.
                Please contact system administrator."""
                html_code = flask.render_template('error.html',
                                err_msg = data)
        else:
            data = """ There was a server error while changing program name.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit/description', methods=['GET', 'POST'])
def edit_program_desc():
    pgm_id = flask.request.args.get('program_id')
    print('program id: ', pgm_id)

    if not modify_database.existingProgramID(pgm_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    elif flask.request.method == 'POST':
        # get new desc from text input field
        new_program_desc = flask.request.form['new_pgm_desc']
        print('Got new program desc! :', new_program_desc)

        if modify_database.existingProgramID(pgm_id):
            success, message = modify_database.change_program_desc(pgm_id, new_program_desc)
        else:
            data = """ Invalid program id.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

        if success: # if successfully changed program name
            status, data = access_database.get_program_details(pgm_id)
            if status:
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                data = """ There was a server error while getting program details.
                Please contact system administrator."""
                html_code = flask.render_template('error.html',
                                err_msg = data)
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

    if not modify_database.existingProgramID(pgm_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    elif flask.request.method == 'POST':
        # get new desc from text input field
        new_program_avail = flask.request.form['new_pgm_avail']
        print('Got new program avail! :', new_program_avail)

        success, message = modify_database.change_program_avail(pgm_id, new_program_avail)

        if success: # if successfully changed program name
            status, data = access_database.get_program_details(pgm_id)
            if status:
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                data = """ There was a server error while getting program details.
                Please contact system administrator."""
                html_code = flask.render_template('error.html',
                                err_msg = data)
        else:
            data = """ There was a server error while changing program availability.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit/module_seq', methods=['GET', 'POST'])
def edit_module_seq():
    print("Currently in oea.py: edit_module_seq" + '\n')
    pgm_id = flask.request.args.get('program_id')
    print('modules page program id = ', pgm_id)

    if not modify_database.existingProgramID(pgm_id):
        data = """ There was a server error while getting program details.
                Please contact system administrator."""
        html_code = flask.render_template('error.html',
                        err_msg = data)

    elif flask.request.method == 'POST':
        # num_modules = flask.request.form['num_modules']
        for name, val in flask.request.form.items():
            print('name = ', name)
            print('val = ', val)
            status, msg = modify_database.change_module_idx(name, val)
            print('status of changing idx = ', status)

            if not status:
                data = """ There was a server error while creating program id.
                Please contact system administrator."""
                return errorResponse(data)

            # get module id from flask req
            # get new idx from flask req
            # call database function to update
    success, data = access_database.get_program_details(pgm_id)
    if success:
        print("data retrieved:", data)
        html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
    else:
        data = """ There was a server error while getting program details.
                Please contact system administrator."""
        html_code = flask.render_template('error.html',
                        err_msg = data)

    response = flask.make_response(html_code)
    return response

# DISPLAY LIST OF MODULES FOR SPECIFIC PROGRAM
@app.route('/admin/programs/modules', methods=['GET'])
def get_modules_of_program():

    username = auth.authenticate()
    authorize_admin(username)

    program_id = flask.request.args.get('program_id')
    print('modules page program id = ', program_id)

    if not modify_database.existingProgramID(program_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    status, data = access_database.get_program_details(program_id)
    print('modules list: ', data['modules'])

    if status:
        print("Got modules list for program")
        html_code = flask.render_template('admin_modules.html',
                                          program_name = data['program_name'], program_id = program_id,
                                          moduleslist = data['modules'], username=username)
    else:
        data = """ There was a server error while getting program details.
        Please contact system administrator."""
        html_code = flask.render_template('error.html', err_msg = data)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/modules/edit/name', methods=['GET', 'POST'])
def edit_module_name():
    module_id = flask.request.args.get('module_id')

    if not modify_database.existingModuleID(module_id):
        print('inside check function of nonexistant module id')
        message = "Invalid module id. Please contact system administrator."
        return errorResponse(message)

    elif module_id == "":
        print("module_id is none")
    print('GET get MODULE_ID', module_id)
    program_id = flask.request.args.get('program_id')
    print('program_id = ', program_id)

    if not modify_database.existingProgramID(program_id):
            print('inside invalid program id check')
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    elif flask.request.method == 'POST':
        new_module_name = flask.request.form['new_module_name']
        print('post get new module name: ', new_module_name)

        success, message = modify_database.change_module_name(module_id, new_module_name )
        if success: # if successfully changed module name
            print('PROGRAM ID FOR MOD = ', program_id)
            success, data = access_database.get_program_details(program_id)
            if success:
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                data = """ There was a server error while getting program details.
                Please contact system administrator."""
                html_code = flask.render_template('error.html',
                                err_msg = data)
        else:
            data = """ There was a server error while changing module name.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/modules/edit/link', methods=['GET','POST'])
def edit_module_link():
    print('entering editing link function...')
    module_id = flask.request.args.get('module_id')

    if not modify_database.existingModuleID(module_id):
        message = "Invalid module id. Please contact system administrator."
        return errorResponse(message)

    print('module id = ', module_id)
    program_id  = flask.request.args.get('program_id')
    print('program_id = ', program_id)

    if not modify_database.existingProgramID(program_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    elif flask.request.method == 'POST':
        new_module_link = flask.request.form['new_module_link']
        print('new_module_link = ', new_module_link)

        success, message = modify_database.edit_module_link(new_module_link, module_id)

        if success:
            print("Modifying module link to: ", new_module_link)
            success, data = access_database.get_program_details(program_id)
            if success:
                print('Changed module link to: ', new_module_link)
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                data = """ There was a server error while getting program details.
                Please contact system administrator."""
                html_code = flask.render_template('error.html',
                                err_msg = data)

        else:
            data = """ There was a server error while editing module link.
            Please contact system administrator."""
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/delete/program', methods=['POST'])
def delete_program():
    program_id = flask.request.args.get('program_id')
    if not modify_database.existingProgramID(program_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    print('program_id = ', program_id)
    success, message = modify_database.delete_program(program_id)

    if success:
        status, data = access_database.get_programslist()
        if status:
            print("Admin Interface: displaying programs list")
            html_code = flask.render_template('admin_programs.html',
                        programslist = data)
        else:
            print("Error: " + data)
            html_code= flask.render_template('error.html',
                        err_msg = data)

    else:
        data = """ There was a server error while deleting program.
        Please contact system administrator."""
        html_code = flask.render_template('error.html',
                            err_msg = data)
    response = flask.make_response(html_code)
    return response


@app.route('/admin/programs/modules/delete', methods=['POST'])
def delete_module():
    module_id = flask.request.args.get('module_id')
    print('module_id', module_id)

    if not modify_database.existingModuleID(module_id):
        message = "Invalid module id. Please contact system administrator."
        return errorResponse(message)

    program_id = flask.request.args.get('program_id')
    print('program_id', program_id)

    if not modify_database.existingProgramID(program_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    success, message = modify_database.delete_module(module_id)
    print("deleting module success = ", success)

    if success:
        print(message)
        success, data = access_database.get_program_details(program_id)
        print("success of getting program details = ", success)
        if success:
            print("modules of program:", data['modules'])
            html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
        else:
            data = """ There was a server error while getting program details.
        Please contact system administrator."""
            html_code = flask.render_template('error.html',
                            err_msg = data)
    else:
        data = """ There was a server error while deleting module.
        Please contact system administrator."""
        html_code = flask.render_template('error.html',
                            err_msg = data)
    response = flask.make_response(html_code)
    return response

@app.route('/student', methods=['GET'])
def student_interface():
    username = auth.authenticate()
    authorize_student(username)

    status, studentid = access_database.get_student_id(username)
    status, student_info = access_database.get_student_info(studentid)
    if status:
        print("Student Interface: displaying programs list for " + str(username))
        html_code = flask.render_template('student_interface.html',
                    student_info = student_info, studentid=studentid, username=student_info['user_name'])
    else:
        data = """ There was a server error while getting student programs.
        Please contact system administrator."""
        html_code = flask.render_template('error_student.html', err_msg= data)
    response = flask.make_response(html_code)
    return response

@app.route('/student/program', methods=['GET'])
def student_program():
    username = auth.authenticate()
    authorize_student(username)

    status, studentid = access_database.get_student_id(username)
    programid = flask.request.args.get('programid')
    print(programid)
    status, programdata = access_database.get_program_details(programid)
    success, program_status = access_database.get_student_program_status(studentid, programid)
    if status and success:
        print("Student Interface: displaying program info " + programid + " for " + str(username))
        print(programdata)
        if program_status == 'enrolled':
            html_code = flask.render_template('student_program.html',
                        program = programdata, availability=program_status, studentid=studentid, username=username)
        elif program_status == 'available':
            html_code = flask.render_template('student_available_program.html',
                        program = programdata, availability=program_status, studentid=studentid, username=username)

        if program_status == 'locked':
            html_code = flask.render_template('student_locked_program.html',
                    program = programdata, availability=program_status, studentid=studentid, username=username)

    elif(not status):
        data = """ There was a server error while getting program details.
        Please contact system administrator."""
        html_code = flask.render_template('error_student.html', err_msg=data)
    elif(not success):
        data = """ There was a server error while getting student program status.
        Please contact system administrator."""
        html_code = flask.render_template('error_student.html', err_msg=data)
    response = flask.make_response(html_code)
    return response


@app.route('/student/program/module', methods=['GET'])
def student_program_module():

    username = auth.authenticate()
    authorize_student(username)

    status, studentid= access_database.get_student_id(username)
    moduleid = flask.request.args.get('moduleid')
    print("moduleid", moduleid)

    # for security: need to validate studentid and moduleid before accessing db

    print("current link", request.full_path)
    status, moduledata = access_database.get_module(moduleid)
    # get first incomplete assessment
    # if this module seq is greater than the completed assessment
    # it should be locked

    program_id = moduledata['program_id']
    if not modify_database.existingProgramID(program_id):
            message = "Invalid program id. Please contact system administrator."
            return errorResponse(message)

    success, min_idx = access_database.get_locked_module_index(studentid, program_id) #handle error
    print("last incomplete quiz is module at index", min_idx)
    print(moduledata['module_index'])
    if moduledata['module_index'] > min_idx:
        print("curr_idx greater than min_idx")
        html_code = flask.render_template('error.html',
                    err_msg = "You do not have access to this module.")
        response = flask.make_response(html_code)
        return response

    success, program_status = access_database.get_student_program_status(studentid, program_id)
    if status and program_status == 'enrolled':
        status, programdata = access_database.get_program_details(program_id)
        if status:
            print("Student Interface: displaying module info " + moduleid + " for " + str(username))
            html_code = flask.render_template('student_program_module.html',
                        module = moduledata, program=programdata, studentid=studentid, username=username)
        else:
            data = """ There was a server error while getting program details.
            Please contact system administrator."""
            html_code = flask.render_template('error_student.html', err_msg=data)
    elif(not status or not success):
        data = """ There was a server error while getting student program status.
        Please contact system administrator."""
        html_code = flask.render_template('error_student.html', err_msg="Program " + program_id + " is " + program_status + " please enroll or contact the admin to gain access.")
    response = flask.make_response(html_code)
    return response

@app.route('/completemodule', methods=['GET'])
def student_complete_module():
    studentid = flask.request.args.get('studentid')
    moduleid = flask.request.args.get('moduleid')
    status, msg = modify_database.update_assessment_status(studentid, moduleid, 1)

    if not status:
        data = """ There was a server error while updating assessment status.
        Please contact system administrator."""
        html_code = flask.render_template('error_student.html', err_msg= data)

    return flask.make_response(html_code)


@app.route('/enrollpgm', methods=['GET'])
def student_enroll_program():
    studentid = flask.request.args.get('studentid')
    programid = flask.request.args.get('programid')
    status, msg = modify_database.update_program_status(studentid, programid, "enrolled")
    if not status:
        data = """ There was a server error while updating program status.
        Please contact system administrator."""
        html_code = flask.render_template('error_student.html', err_msg= data)
    return flask.make_response(html_code)


# def main():





# if __name__ == '__main__':
#     main()
