import flask
import access_database
import modify_database

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
@app.route('/admin_interface', methods=['GET'])
def admin_interface():
    html_code = flask.render_template('admin_interface.html')
    response = flask.make_response(html_code)
    return response

# admin
@app.route('/students', methods=['GET'])
def student_interface():
    html_code = flask.render_template('admin_students.html')
    response = flask.make_response(html_code)
    return response

@app.route('/programs', methods=['GET'])
def admin_programs():
    # programslist is a tuple
    # programslist[0] indicates whether data was retrieved successfully
    programslist = access_database.get_all_programs()
    if programslist[0] is True:
        print("Admin Interface: displaying programs list")
        html_code = flask.render_template('admin_programs.html',
                    programslist = programslist[1])
    response = flask.make_response(html_code)
    return response

@app.route('/create_program', methods=['POST'])
def admin_create_program():
    html_code = flask.render_template('admin_create_program.html')
    response = flask.make_response(html_code)
    return response

