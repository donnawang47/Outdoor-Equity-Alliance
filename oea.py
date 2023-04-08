import flask
import access_database
import modify_database
import display_database

app = flask.Flask(__name__, template_folder=".")

# temporary main page
# not sure what it should be
@app.route('/', methods=["GET"])
@app.route('/index', methods=['GET'])
def index():
    html_code = flask.render_template('index.html')
    response = flask.make_response(html_code)
    return response


# admin interface main page
# menu for programs page and students page
@app.route('/admin', methods=['GET'])
def admin_interface():
    html_code = flask.render_template('admin_interface.html')
    response = flask.make_response(html_code)
    return response

# admin
@app.route('/admin/students', methods=['GET'])
def admin_students():
    status, students = access_database.get_all_students()

    html_code = flask.render_template('admin_students.html', students=students)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/students/studentdetails', methods=['GET'])
def admin_studentdetails():
    studentid = flask.request.args.get('studentid')
    print("studentid", studentid)

    status, student_programs = access_database.get_student_programs(studentid)
    print("oea: get student programs done")
    # can only get student progress on enrolled programs?
    # need to change to enrolled
    enrolled_pgms = student_programs['Enrolled'] # program ids
    print(enrolled_pgms)
    enrolled_pgms_status = {} # pgm_id : status
    for pgm_id in enrolled_pgms:
        pgm_status = access_database.get_student_program_progress(studentid, pgm_id)
        print("pgm_status" + pgm_status)
        enrolled_pgms_status[pgm_id] = pgm_status


    print("oea.py, enrolled_pgms_status:", enrolled_pgms_status)

    print("Student Interface: displaying programs list")
    html_code = flask.render_template('admin_studentdetails.html',
                studentid = studentid,
                programs = student_programs,
                enrolled_pgms_status = enrolled_pgms_status)
    response = flask.make_response(html_code)
    return response

# doesnt produce new page
@app.route('/admin/students/studentdetails/updatePgmStatus', methods=['GET'])
def admin_updatePgmStatus():
    print("updating program status")
    studentid = flask.request.args.get('studentid')
    print("studentid", studentid)
    pgm_id = flask.request.args.get('pgm_id')
    print("pgm_id", pgm_id)
    pgm_status = flask.request.args.get('pgm_status')

    status, msg = modify_database.update_program_status(studentid, pgm_id, pgm_status)
    print("oea:", msg)
    html_code = flask.render_template('admin_edit_pgm_status_btn.html',
                studentid = studentid,
                pgm = pgm_id,)
    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs', methods=['GET'])
def admin_programs():
    # programslist is a tuple
    # programslist[0] indicates whether data was retrieved successfully
    status, programslist = access_database.get_programslist()
    if status is True:
        print("Admin Interface: displaying programs list")
        html_code = flask.render_template('admin_programs.html',
                    programslist = programslist)
    else:
        print("Error: " + programslist)
        #html_code=""
    response = flask.make_response(html_code)

    return response

@app.route('/admin/programs/create_program', methods=['GET','POST'])
def admin_create_program():
    if flask.request.method == 'POST':
        pgm_params = {}
        # create program_id
        pgm_params["program_id"] = modify_database.create_program_id()
        pgm_params["program_name"] = flask.request.form['pgm_name']
        pgm_params["description"] = flask.request.form['pgm_descrip']
        pgm_params["program_availability"] = flask.request.form['pgm_avail']

        success = modify_database.insert_program(pgm_params)
        if success:
            print("new program inserted")
            # display_database.main()

        # iterate this multiple times if multiple modules?
        # modules_params
        md_params = {}
        md_params["module_id"] = modify_database.create_module_id()
        md_params["program_id"] = pgm_params["program_id"]
        md_params["module_name"] = flask.request.form['module_name']
        md_params["content_link"] = flask.request.form['module_link']
        md_params["content_type"] = flask.request.form['module_type']
        md_params["module_index"] = flask.request.form['module_seq']

        success = modify_database.insert_module(md_params)
        if success:
            print("new module inserted")
            display_database.main()

    html_code = flask.render_template('admin_create_program.html')
    response = flask.make_response(html_code)
    return response

@app.route("/admin/programs/create_module", methods=['GET', 'POST'])
def admin_create_module():
    program_id = flask.request.args.get('program_id')
    if flask.request.method == 'POST':
        # modules_params
        md_params = {}
        md_params["module_id"] = modify_database.create_module_id()
        md_params["program_id"] = program_id
        md_params["module_name"] = flask.request.form['module_name']
        md_params["content_link"] = flask.request.form['content_link']
        md_params["content_type"] = flask.request.form['content_type']
        md_params["module_index"] = flask.request.form['index']

        success = modify_database.insert_module(md_params)
        if success:
            print("new module inserted")
            display_database.main()
        else:
            html_code = flask.render_template('error.html', )
    else:
        program_name = flask.request.args.get('program_name')
        html_code = flask.render_template('admin_create_module.html', program_name)

    response = flask.make_response(html_code)
    return response

#TODO: ASK why we can reference html_code outside of scope?
@app.route('/admin/programs/edit/name', methods=['GET', 'POST'])
def edit_program_name():

    id = flask.request.args.get('program_id')
    print('program id: ', id)

    if flask.request.method == 'POST' and id is not None:
        # get new name from text input field
        new_program_name = flask.request.form['new_program_name']
        print('Got new program name! :', new_program_name)

        success, message = modify_database.change_program_name(id, new_program_name)

        if success: # if successfully changed program name
            status, programslist = access_database.get_programslist()
            if status:
                print('Display program list with updated program name')
                html_code = flask.render_template('admin_programs.html',
                            programslist = programslist)
        elif not success or not status:
            html_code = flask.render_template('error.html',
                                err_msg = message)

    # display initial access to "edit program page" for specific program
    else:
        program_name = flask.request.args.get('program_name')
        html_code = flask.render_template('admin_edit_program.html',
                                    program_id = id,
                                    program_name=program_name)

    response = flask.make_response(html_code)
    return response

# DISPLAY LIST OF MODULES FOR SPECIFIC PROGRAM
@app.route('/admin/modules', methods=['GET'])
def get_modules_of_program():
    program_id = flask.request.args.get('program_id')
    program_name = flask.request.args.get('program_name')

    status, data = access_database.get_program_modules(program_id)
    moduleslist = data['modules']
    print('modules list: ', moduleslist)

    if status:
        print("Got modules list for program")
        html_code = flask.render_template('admin_modules.html',
                                          program_name = program_name, program_id = program_id,
                                          moduleslist = moduleslist)
    else:
        html_code = flask.render_template('error.html', err_msg = moduleslist)

    response = flask.make_response(html_code)
    return response

# DISPLAY EDITING PAGE FOR SPECIFIC MODULE AFTER CLICKING EDIT BUTTON
@app.route('/admin/modules/edit/name', methods=['GET', 'POST'])
def edit_module_name():
    # from URL of admin_module_edit_module.html
    module_id = flask.request.args.get('module_id')
    if module_id == "":
        print("module_id is none")
    print('GET get MODULE_ID', module_id)
    program_id = flask.request.args.get('program_id')
    print('program_id = ', program_id)
    program_name = flask.request.args.get('program_name')
    print('program_name: ', program_name)

    if flask.request.method == 'POST' and program_id != "" and module_id != "" and program_name != "":
        new_module_name = flask.request.form['new_module_name']
        print('post get new module name: ', new_module_name)

        success, message = modify_database.change_module_name(module_id, new_module_name )

        if success: # if successfully changed module name
            print('PROGRAM ID FOR MOD = ', program_id)
            status, data = access_database.get_program_modules(program_id)
            print('DATA = ', data)
            moduleslist = data['modules']
            print('TEST A modulelist = ', moduleslist)
            if status:
                print('Changed module name to: ', new_module_name)
                html_code = flask.render_template('admin_modules.html',
                            moduleslist = moduleslist,
                            program_name = program_name,
                            program_id=program_id)
        elif not success or not status:
            html_code = flask.render_template('error.html',
                                err_msg = message)

    # display initial access to "edit program page" for specific program
    else:
        module_name = flask.request.args.get('module_name')
        print( 'MODULE NAME: ', module_name)
        html_code = flask.render_template('admin_edit_module.html', module_name=module_name, module_id = module_id,program_id = program_id, program_name = program_name)

    response = flask.make_response(html_code)
    return response



# @app.route('/edit_module_link', methods=['POST'])
# def edit_module_link(new_module_link):
#     new_module_link = flask.request.args.get('new_module_link')
#     module_name = flask.request.args.get('module_name')
#     result = modify_database.change_program_name(new_module_link, module_name)

#     if result:
#         print("Changed module link to: ", new_module_link)
#     else:
#         print("A server error occurred. Please contact the system administrator.")


# @app.route('/edit_module_name', methods=['POST'])
# def edit_module_name():
#     new_module_name = flask.request.args.get('new_module_name')
#     module_name = flask.request.args.get('module_name')
#     result = modify_database.change_module_name(new_module_name, module_name)

#     if result:
#         print("Changed program name to: ", new_module_name)
#         html_code = flask.render_template('admin_edit_module.html',
#                                         program_name = new_module_name)
#         response = flask.make_response(html_code)
#         return response


@app.route('/student', methods=['GET'])
def student_interface():
    status, student_programs = access_database.get_student_programs(2)
    if status:
        print("Student Interface: displaying programs list")
        html_code = flask.render_template('student_interface.html',
                    programs = student_programs)
    else:
        html_code = flask.render_template('error.html', err_msg=student_programs)
    response = flask.make_response(html_code)
    return response

@app.route('/student/program', methods=['GET'])
def student_program():
    programid = flask.request.args.get('programid')
    print(programid)
    status, programdata = access_database.get_program_modules(programid)
    if status:
        print("Student Interface: displaying program info " + programid + " for ")
        html_code = flask.render_template('student_program.html',
                    program = programdata)
    else:
        html_code = flask.render_template('error.html', err_msg=programdata)
    response = flask.make_response(html_code)
    return response


@app.route('/student/program/module', methods=['GET'])
def student_program_module():
    moduleid = flask.request.args.get('moduleid')
    print(moduleid)
    status, moduledata = access_database.get_module(moduleid)
    status, programdata = access_database.get_program_modules(moduledata['program_id'])
    if status:
        print("Student Interface: displaying module info " + moduleid + " for ")
        html_code = flask.render_template('student_program_module.html',
                    module = moduledata, program=programdata)
    else:
        html_code = flask.render_template('error.html', err_msg=moduledata)
    response = flask.make_response(html_code)
    return response

