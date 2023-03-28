import flask
import access_database
import modify_database

app = flask.Flask(__name__, template_folder=".")

@app.route('/', methods=["GET"])
@app.route('/index', methods=['GET'])
def index():
    html_code = flask.render_template('index.html')
    response = flask.make_response(html_code)
    return response





@app.route('/admin_interface', methods=['GET'])
def admin_interface():
    html_code = flask.render_template('admin_interface.html')
    response = flask.make_response(html_code)
    return response


@app.route('/students', methods=['GET'])
def student_interface():
    html_code = flask.render_template('student_page.html')
    response = flask.make_response(html_code)
    return response

@app.route('/programs', methods=['GET'])
def admin_interface_programs():
    # programslist is a tuple
    # programslist[0] indicates whether data was retrieved successfully
    programslist = access_database.get_all_programs()
    if programslist[0] is True:
        print("Admin Interface: displaying programs list")
        html_code = flask.render_template('programs_page.html',
                    programslist = programslist[1])
    response = flask.make_response(html_code)
    return response

