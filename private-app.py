from flask import Flask, jsonify
import requests

app = Flask(__name__)

PRIVATE_APP_ACCESS = ''

@app.route('/')
def get_companies():
    companies_url = 'https://api.hubspot.com/crm/v3/objects/companies'
    headers = {
        'Authorization': f'Bearer {PRIVATE_APP_ACCESS}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(companies_url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return jsonify(response.json().get('results'))
    except requests.exceptions.RequestException as error:
        print(error)
        return jsonify({'error': str(error)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=3000)
