import os
import sys
import json
import requests
import flask
import oauthlib.oauth2
import database

GOOGLE_DISCOVERY_URL = ('https://accounts.google.com/.well-known/openid-configuration')
GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']

client = oauthlib.oauth2.WebApplicationClient(GOOGLE_CLIENT_ID)


def login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = (google_provider_cfg['authorization_endpoint'])

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri = flask.request.base_url + '/callback',
        scope=['openid', 'email', 'profile'],
    )

    print('request_uri:', request_uri, file=sys.stderr)

    return flask.redirect(request_uri)

def callback():
    code = flask.request.args.get('code')

    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()

    token_endpoint = google_provider_cfg['token_endpoint']
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=flask.request.url,
        redirect_url=flask.request.base_url,
        code=code
    )

    #fetch tokens
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    #parse tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    #get user info with tokens
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if not userinfo_response.json().get('email_verified'):
        message = 'User email not available or not verified by Google.'
        return message, 400

    #save profile data
    flask.session['sub'] = userinfo_response.json()['sub']
    flask.session['name'] = userinfo_response.json()['name']
    flask.session['given_name'] = userinfo_response.json()['given_name']
    flask.session['picture'] = userinfo_response.json()['picture']
    flask.session['email'] = userinfo_response.json()['email']
    flask.session['email_verified'] = userinfo_response.json()['email_verified']
    flask.session['locale'] = userinfo_response.json()['locale']


    username = flask.session['email']
    success, isAdmin = database.is_admin_authorized(username)
    if success and isAdmin:
        print("is admin")
        return flask.redirect(flask.url_for('admin_interface'))
    success, isStudent = database.is_student_authorized(username)
    if success and isStudent:
        print("is student")
        return flask.redirect(flask.url_for('student_interface'))

    print("not authorized")
    return flask.redirect(flask.url_for('index'))

def logout():
    flask.session.clear()
    html_code = flask.render_template('loggedout.html')
    response = flask.make_response(html_code)
    return response

def authenticate():
    if 'email' not in flask.session:
        flask.abort(flask.redirect(flask.url_for('login')))
    return flask.session.get('email')



