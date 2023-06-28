import os
from flask import Flask, render_template, redirect, request
import requests

app = Flask(__name__)
app.secret_key = os.urandom(16).hex()

CLIENT_ID = ''
CLIENT_SECRET = ''

REDIRECT_URI = 'http://localhost:5000/oauth-callback'

auth_url = ''
token_store = {}


def is_authorized(user_id):
    return True if user_id in token_store else False


@app.route('/')
def index():
    session_id = request.cookies.get('sessionid')
    if is_authorized(session_id):
        access_token = token_store[session_id]
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        contacts_url = 'https://api.hubapi.com/crm/v3/objects/contacts'
        try:
            response = requests.get(contacts_url, headers=headers)
            data = response.json()
            print(data['results'][0])
            return render_template('home.html', token=access_token, contacts=data['results'])
        except Exception as e:
            print(e)
    else:
        print("4")
        return render_template('home.html', auth_url=auth_url)


@app.route('/oauth-callback')
def oauth_callback():
    auth_code = request.args.get('code')
    auth_code_proof = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': auth_code
    }
    try:
        response = requests.post('https://api.hubapi.com/oauth/v1/token', data=auth_code_proof)
        response_body = response.json()
        session_id = request.cookies.get('sessionid')
        token_store[session_id] = response_body['access_token']
        return redirect('/')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(port=5000)
