from flask import Flask, request, jsonify
import base64
import subprocess
import os
import json


app = Flask(__name__)



USERS_FILE = 'users.json'

def get_users():
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []
    
    return users

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if 'name' not in data or 'email' not in data or 'phone' not in data or 'password' not in data:
        return jsonify({'error': 'missing fields'}), 400
    
    users = get_users()
    
    for user in users:
        if user['email'] == data['email']:
            return jsonify({'error': 'user already exists'}), 409
    
    user = {
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'password': data['password']
    }
    
    users.append(user)
    
    save_users(users)
    
    return jsonify({'message': 'signup successful'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'missing fields'}), 400
    
    users = get_users()
    
    for user in users:
        if user['email'] == data['email'] and user['password'] == data['password']:
            return jsonify({'message': 'login successful'}), 200
    
    return jsonify({'error': 'invalid credentials'}), 401





@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    # check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'no file found'}), 400
    
    file = request.files['file']
    
    # convert file data to base64
    file_data = file.read()
    file_base64 = base64.b64encode(file_data).decode('utf-8')
    
    # write base64 data to a file in binary format
    with open('output.pdf', 'wb') as f:
        f.write(base64.b64decode(file_base64))
    
    # run the command in the background with file path as argument
    subprocess.Popen(['python3', 'pdf2text.py', 'output.pdf']).wait()
    
    # delete the file
    os.remove('output.pdf')
    
    return jsonify({'message': 'processing complete'}), 200

if __name__ == '__main__':
    app.run(debug=True)
