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

@app.route('/admin/programs', methods=['GET'])
def admin_programs():
    # programslist is a tuple
    # programslist[0] indicates whether data was retrieved successfully
    status, programslist = access_database.get_all_programs()
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
        pgm_params["program_id"] = modify_database.create_module_id()
        md_params["module_name"] = flask.request.form['module_name']
        md_params["module_link"] = flask.request.form['module_link']
        md_params["module_type"] = flask.request.form['module_type']
        md_params["module_seq"] = flask.request.form['module_seq']

        success = modify_database.insert_module(md_params)
        if success:
            print("new module inserted")
            display_database.main()

    html_code = flask.render_template('admin_create_program.html')
    response = flask.make_response(html_code)
    return response

@app.route('/student', methods=['GET'])
def student_interface():
    student_programs = access_database.get_student_programs(2)
    if True:
        print("Student Interface: displaying programs list")
        html_code = flask.render_template('student_interface.html',
                    programs = student_programs)
    response = flask.make_response(html_code)
    return response


