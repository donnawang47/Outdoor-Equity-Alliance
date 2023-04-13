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

@app.route('/admin/students/studentdetails', methods=['GET','POST'])
def admin_studentdetails():
    studentid = flask.request.args.get('studentid')
    print("studentid", studentid)

    if flask.request.args.get('updateStatus') == 'true':
        id = flask.request.args.get('id')
        category = flask.request.args.get('category')
        print("id", id)
        if flask.request.method == 'POST':
            if category == 'program':
                pgm_status = flask.request.form['pgm_status']
                status, msg = modify_database.update_program_status(studentid, id, pgm_status)
                print("oea updating program status:", msg)
            elif category == 'module':
                mod_status = flask.request.form['mod_status']
                status, msg = modify_database.update_assessment_status(studentid, id, mod_status)
                print("oea updating module status:", msg)


    status, student_programs = access_database.get_student_programs(studentid)
    status, student_info = access_database.get_student_info(studentid)
    print("oea: get student programs done")
    # can only get student progress on enrolled programs?
    # need to change to enrolled
    enrolled = student_programs['Enrolled'] # program ids
    print(enrolled)
    enrolled_pgms = {} # pgm_id : status
    for pgm_id in enrolled:
        pgm = {}
        success, pgm_status = access_database.get_student_program_progress(studentid, pgm_id)
        print("pgm_status" + pgm_status)
        pgm['pgm_status'] = pgm_status
        status, data = access_database.get_program_details(pgm_id)
        assessments = []
        for mod in data['modules']:
            print(mod)
            if mod['content_type'] == 'assessment':
                assessments.append((mod['module_id'], student_info[mod['module_id']]))
        pgm['assessments'] = assessments
        enrolled_pgms[pgm_id] = pgm


    print("oea.py, enrolled_pgms:", enrolled_pgms)

    print("Student Interface: displaying programs list")
    html_code = flask.render_template('admin_studentdetails.html',
                studentid = studentid,
                programs = student_programs,
                enrolled_pgms = enrolled_pgms)
    response = flask.make_response(html_code)
    return response

# doesnt produce new page
@app.route('/admin/students/studentdetails/updatePgmStatus', methods=['GET','POST'])
def admin_updatePgmStatus():
    print("updating program status")
    studentid = flask.request.args.get('studentid')
    print("studentid", studentid)
    pgm_id = flask.request.args.get('pgm_id')
    print("pgm_id", pgm_id)

    if flask.request.method == 'POST':
        pgm_status = flask.request.form['pgm_status']
        status, msg = modify_database.update_program_status(studentid, pgm_id, pgm_status)
        print("oea updating program status:", msg)
        html_code = flask.render_template('admin_edit_pgm_status_btn.html')
    else:
        html_code = flask.render_template('error.html', err_msg = "error has occurred")
    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs', methods=['GET'])
def admin_programs():
    # programslist is a tuple
    # programslist[0] indicates whether data was retrieved successfully
    status, data = access_database.get_programslist()
    if status:
        print("Admin Interface: displaying programs list")
        html_code = flask.render_template('admin_programs.html',
                    programslist = data)
    else:
        print("Error: " + programslist)
        html_code= flask.render_template('error.html',
                    err_msg = data)

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

        success, message = modify_database.insert_program(pgm_params)
        status, programslist = access_database.get_programslist()

        if success:
            print("new program inserted")
            html_code = flask.render_template('admin_programs.html',
                                        programslist = programslist)
        elif not success:
            html_code = flask.render_template('error.html',
                                err_msg = "A server error occurred while inserting program.")
        elif not status:
            html_code = flask.render_template('error.html',
                                    err_msg = "A server error occurred while getting programs list.")
    else:
        html_code = flask.render_template('admin_create_program.html')
            # display_database.main()

        # # iterate this multiple times if multiple modules?
        # # modules_params
        # md_params = {}
        # md_params["module_id"] = modify_database.create_module_id()
        # md_params["program_id"] = pgm_params["program_id"]
        # md_params["module_name"] = flask.request.form['module_name']
        # md_params["content_link"] = flask.request.form['module_link']
        # md_params["content_type"] = flask.request.form['module_type']
        # md_params["module_index"] = flask.request.form['module_seq']

        # success = modify_database.insert_module(md_params)
        # if success:
        #     print("new module inserted")
        #     display_database.main()

    # html_code = flask.render_template('admin_create_program.html')
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

@app.route('/admin/programs/edit', methods=['GET', 'POST'])
def admin_edit_program():
    pgm_id = flask.request.args.get('program_id')
    print('program id: ', id)

    success, data = access_database.get_program_details(pgm_id)
    if success:
        print("data retrieved:",data)
        html_code = flask.render_template('admin_programdetails.html',
                            pgm_data = data,
                            moduleslist = data['modules'])
    else:
        html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response

#TODO: ASK why we can reference html_code outside of scope?
@app.route('/admin/programs/edit/name', methods=['GET', 'POST'])
def edit_program_name():

    pgm_id = flask.request.args.get('program_id')
    print('program id: ', id)

    if flask.request.method == 'POST':
        # get new name from text input field
        new_program_name = flask.request.form['new_program_name']
        print('Got new program name! :', new_program_name)

        success, message = modify_database.change_program_name(pgm_id, new_program_name)

        if success: # if successfully changed program name
            status, data = access_database.get_program_details(pgm_id)
            if success:
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                html_code = flask.render_template('error.html',
                                err_msg = data)
        else:
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit/description', methods=['GET', 'POST'])
def edit_program_desc():
    pgm_id = flask.request.args.get('program_id')
    print('program id: ', pgm_id)

    if flask.request.method == 'POST':
        # get new desc from text input field
        new_program_desc = flask.request.form['new_pgm_desc']
        print('Got new program desc! :', new_program_desc)

        success, message = modify_database.change_program_desc(pgm_id, new_program_desc)

        if success: # if successfully changed program name
            status, data = access_database.get_program_details(pgm_id)
            if success:
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                html_code = flask.render_template('error.html',
                                err_msg = data)
        else:
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/edit/availability', methods=['GET', 'POST'])
def edit_program_avail():
    pgm_id = flask.request.args.get('program_id')
    print('program id: ', pgm_id)

    if flask.request.method == 'POST':
        # get new desc from text input field
        new_program_avail = flask.request.form['new_pgm_avail']
        print('Got new program avail! :', new_program_avail)

        success, message = modify_database.change_program_avail(pgm_id, new_program_avail)

        if success: # if successfully changed program name
            status, data = access_database.get_program_details(pgm_id)
            if success:
                print("data retrieved:",data)
                html_code = flask.render_template('admin_programdetails.html', pgm_data = data, moduleslist = data['modules'])
            else:
                html_code = flask.render_template('error.html',
                                err_msg = data)
        else:
            html_code = flask.render_template('error.html',
                                err_msg = data)

    response = flask.make_response(html_code)
    return response

# DISPLAY LIST OF MODULES FOR SPECIFIC PROGRAM
@app.route('/admin/modules', methods=['GET'])
def get_modules_of_program():
    program_id = flask.request.args.get('program_id')
    print('modules page program id = ', program_id)
    program_name = flask.request.args.get('program_name')
    print('modules page program name = ', program_name)

    status, data = access_database.get_program_details(program_id)
    print('modules list: ', data['modules'])

    if status:
        print("Got modules list for program")
        html_code = flask.render_template('admin_modules.html',
                                          program_name = program_name, program_id = program_id,
                                          moduleslist = data['modules'])
    else:
        html_code = flask.render_template('error.html', err_msg = data)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/modules/edit/sequence', methods=['GET', 'POST'])
def edit_module_seq():
    print("oea.py: edit_module_seq")
    program_id = flask.request.args.get('program_id')
    print('modules page program id = ', program_id)
    program_name = flask.request.args.get('program_name')
    print('modules page program name = ', program_name)

    status, data = access_database.get_program_details(program_id)
    print('modules list: ', data['modules'])

    if flask.request.method == 'POST':
        # num_modules = flask.request.form['num_modules']
        for name, val in flask.request.form.items():
            print(name, val)
            modify_database.change_module_idx(name, val)

            # get module id from flask req
            # get new idx from flask req
            # call database function to update
    if status:
        print("Got modules list for program")
        html_code = flask.render_template('admin_modules.html',
                                          program_name = program_name, program_id = program_id,
                                          moduleslist = data['modules'])
    else:
        html_code = flask.render_template('error.html', err_msg = data)

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
            status, data = access_database.get_program_details(program_id)
            print('DATA = ', data)
            modules_list = data['modules']
            print('TEST A modulelist = ', modules_list)
            if status:
                print('Changed module name to: ', new_module_name)
                html_code = flask.render_template('admin_modules.html', moduleslist = modules_list, module_id = module_id,
                                            program_name = program_name, program_id=program_id)
        elif not success or not status:
            html_code = flask.render_template('error.html',
                                err_msg = message)

    # display initial access to "edit program page" for specific program
    else:
        module_name = flask.request.args.get('module_name')
        print( 'MODULE NAME: ', module_name)
        html_code = flask.render_template('admin_edit_module.html', module_name=module_name, module_id = module_id, program_id = program_id, program_name = program_name)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/modules/edit/link', methods=['POST'])
def edit_module_link():
    print('entering editing link function...')
    module_id = flask.request.args.get('module_id')
    print('module id = ', module_id)
    program_id  = flask.request.args.get('program_id')
    print('program_id = ', program_id)
    program_name = flask.request.args.get('program_name')
    print('program_name = ', program_name)
    new_module_link = flask.request.form['new_module_link']
    print('new_module_link = ', new_module_link)

    success, message = modify_database.edit_module_link(new_module_link, module_id)

    if success:
        print("Modifying module link to: ", new_module_link)
        status, data = access_database.get_program_details(program_id)
        modules_list = data['modules']
        if status:
            print('Changed module link to: ', new_module_link)
            html_code = flask.render_template('admin_modules.html', moduleslist = modules_list, module_id = module_id,
                                        program_name = program_name, program_id=program_id)
    elif not success or not status:
        html_code = flask.render_template('error.html',
                            err_msg = message)

    response = flask.make_response(html_code)
    return response

@app.route('/admin/programs/delete/program', methods=['POST'])
def delete_program():
    program_id = flask.request.args.get('program_id')
    print('program_id = ', program_id)
    success, message = modify_database.delete_program(program_id)

    if success:
        status, programslist = access_database.get_programslist()
        if status:
             html_code = flask.render_template('admin_programs.html',
                    programslist = programslist)

    elif not success:
        html_code = flask.render_template('error.html',
                            err_msg = "There was an error while deleting program.")
    elif not status:
        html_code = flask.render_template('error.html',
                                        err_msg = 'There was an error while getting list of programs.')

    response = flask.make_response(html_code)
    return response

def get_current_student():
    return 2

@app.route('/student', methods=['GET'])
def student_interface():
    studentid = get_current_student()
    status, student_programs = access_database.get_student_programs(studentid)
    if status:
        print("Student Interface: displaying programs list for " + str(studentid))
        html_code = flask.render_template('student_interface.html',
                    programs = student_programs, studentid=studentid)
    else:
        html_code = flask.render_template('error_student.html', err_msg=student_programs)
    response = flask.make_response(html_code)
    return response

@app.route('/student/program', methods=['GET'])
def student_program():
    studentid = get_current_student()
    programid = flask.request.args.get('programid')
    print(programid)
    status, programdata = access_database.get_program_details(programid)
    status, program_status = access_database.get_student_program_status(studentid, programid)
    if status:
        print("Student Interface: displaying program info " + programid + " for " + str(studentid))
        html_code = flask.render_template('student_program.html',
                    program = programdata, availability=program_status, studentid=studentid)
    else:
        html_code = flask.render_template('error_student.html', err_msg=programdata)
    response = flask.make_response(html_code)
    return response


@app.route('/student/program/module', methods=['GET'])
def student_program_module():
    studentid=get_current_student()
    moduleid = flask.request.args.get('moduleid')
    print(moduleid)
    status, moduledata = access_database.get_module(moduleid)
    status, program_status = access_database.get_student_program_status(studentid, moduledata['program_id'])
    if program_status == 'enrolled':
        status, programdata = access_database.get_program_details(moduledata['program_id'])
        if status:
            print("Student Interface: displaying module info " + moduleid + " for " + str(studentid))
            html_code = flask.render_template('student_program_module.html',
                        module = moduledata, program=programdata, studentid=studentid)
        else:
            html_code = flask.render_template('error_student.html', err_msg=moduledata)
    else:
        html_code = flask.render_template('error_student.html', err_msg="Program " + moduledata['program_id'] + " is " + program_status + " please enroll or contact the admin to gain access.")
    response = flask.make_response(html_code)
    return response

@app.route('/completemodule', methods=['GET'])
def student_complete_module():
    studentid = flask.request.args.get('studentid')
    moduleid = flask.request.args.get('moduleid')
    status, msg = modify_database.update_assessment_status(studentid, moduleid, 1)
    return flask.make_response("")


@app.route('/enrollpgm', methods=['GET'])
def student_enroll_program():
    studentid = flask.request.args.get('studentid')
    programid = flask.request.args.get('programid')
    status, msg = modify_database.update_program_status(studentid, programid, "enrolled")
    return flask.make_response("")
