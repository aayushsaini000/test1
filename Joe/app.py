from flask import Flask, request, jsonify
import base64
import subprocess
import os
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from flask_cors import CORS
from sqlalchemy import JSON
from flask import jsonify
from datetime import datetime


app = Flask(__name__)
CORS(app)

# Set the configuration of your database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/fileuploader'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database object and initialize the migration object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Process(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    rows = db.Column(JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



def save_to_db(obj):
    # Add and commit to the database
    db.session.add(obj)
    db.session.commit()

def get_users():
    return User.query.all()




@app.route('/get_data/<filename>')
def get_data(filename):
    process = Process.query.filter_by(name=filename).first()
    if process:
        rows = process.rows
        # data = [
        #     {'Name': row[0], 'Address': row[1], 'City/State': row[2], '118': row[3], '119': row[4]}
        #     for row in rows
        # ]
        return jsonify(rows)
    else:
        return jsonify([])



@app.route('/process', methods=['POST'])
def create_process():
    data = request.json
    
    # Create a new Process object
    process_obj = Process(name=data['name'], rows=data['rows'], user_id=5)
    
    # Add the object to the database session
    db.session.add(process_obj)
    
    # Commit the changes to the database
    db.session.commit()
    
    # Return a response indicating success
    return jsonify({'message': 'Process created successfully'}), 201



@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if 'name' not in data or 'email' not in data or 'phone' not in data or 'password' not in data:
        return jsonify({'error': 'missing fields'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({'error': 'user already exists'}), 409
    
    user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        password=data['password']
    )
    
    save_to_db(user)
    
    return jsonify({'message': 'signup successful'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'missing fields'}), 400
    
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        return jsonify({'message': 'login successful'}), 200
    
    return jsonify({'error': 'invalid credentials'}), 401





from werkzeug.utils import secure_filename

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    # check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'no file found'}), 400
    
    file = request.files['file']
    
    # get the filename
    filename = secure_filename(file.filename)
    
    # convert file data to base64
    file_data = file.read()
    file_base64 = base64.b64encode(file_data).decode('utf-8')
    
    # write base64 data to a file in binary format
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(file_base64))
    
    # run the command in the background with file path as argument
    subprocess.Popen(['python3', 'pdf2text.py', filename]).wait()
    
    # delete the file
    os.remove(filename)
    
    return jsonify({'message': 'processing complete'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
