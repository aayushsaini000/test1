from flask import Flask, request, jsonify
import base64
import subprocess
import os

app = Flask(__name__)

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
