from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "list of Endpoints"

#list file in directory
@app.route('/list')
def list():
    pass
    
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

