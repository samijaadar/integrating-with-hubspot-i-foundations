import os
from flask import Flask, request, redirect, render_template
import requests


app = Flask(__name__)
app.secret_key = os.urandom(16)

CLIENT_ID = ''
CLIENT_SECRET = ''

REDIRECT_URI = 'http://localhost:5000/oauth-callback'

auth_url = ''

refresh_token_store = {}
access_token_cache = {}

def is_authorized(user_id):
    return user_id in refresh_token_store

def get_token(user_id):
    if user_id in access_token_cache:
        return access_token_cache[user_id]
    else:
        try:
            refresh_token_proof = {
                'grant_type': 'refresh_token',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'refresh_token': refresh_token_store[user_id]
            }
            response = requests.post('https://api.hubapi.com/oauth/v1/token', data=refresh_token_proof)
            response_data = response.json()
            refresh_token_store[user_id] = response_data['refresh_token']
            access_token_cache[user_id] = response_data['access_token']
            return response_data['access_token']
        except Exception as e:
            print(e)

@app.route('/')
def home():
    session_id = request.cookies.get('sessionid')
    if is_authorized(session_id):
        access_token = get_token(session_id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        contacts_url = 'https://api.hubapi.com/contacts/v1/lists/all/contacts/all'
        try:
            response = requests.get(contacts_url, headers=headers)
            data = response.json()
            return render_template('home.html', token=access_token, contacts=data['contacts'], data=data)
        except Exception as e:
            print(e)
    else:
        return render_template('home.html', auth_url=auth_url)

@app.route('/oauth-callback')
def oauth_callback():
    session_id = request.cookies.get('sessionid')
    auth_code_proof = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': request.args.get('code')
    }
    try:
        response = requests.post('https://api.hubapi.com/oauth/v1/token', data=auth_code_proof)
        response_data = response.json()
        refresh_token_store[session_id] = response_data['access_token']
        access_token_cache[session_id] = response_data['access_token']
        return redirect('/')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.run(port=5000)
