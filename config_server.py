# Guillaume Deconinck & Grynczel Wojciech

# Program launched by program.py

from flask import Flask, render_template, request, url_for, redirect, flash
import configparser
import requests
from model import Model

config_server = Flask(__name__)
config_server.secret_key = 'some_secret'

MODEL = Model()

@config_server.route('/')
def index():
    error = None
    config = {}
    try:
        config = {
         "num":         MODEL.get_value('config')['Checkpoint']['num'],
         "id":          MODEL.get_value('config')['Checkpoint']['id'],
         "url":         MODEL.get_value('config')['Database']['url'],
         "email":       MODEL.get_value('config')['Database']['email'],
         "password":    MODEL.get_value('config')['Database']['password']
        }
        print(str(config))
    except Exception as inst:
        pass

    return render_template('index.html', config=config, error=error)

@config_server.route('/save', methods=['POST'])
def save():
    error = None
    id    = request.form['id']
    num   = request.form['num']
    url   = request.form['url']
    email = request.form['email']
    password = request.form['password']

    if url is not MODEL.get_value('config')['Database']['url']:
        print("Remove id")
        id = None

    print(str(request.form))
    try:
        if id:
            response = requests.patch(url+'/checkpoints/'+id, {"num":num, "email": email, "password": password})
        else:
            response = requests.post(url+'/checkpoints', {"num":num, "email": email, "password": password})

        if response.status_code != 201:
            error = "(" + str(response.text)+ ")"
        else:
            id = response.json()['_id']

    except Exception as inst:
        error = str(inst)
        pass

    MODEL.get_value('config')['Checkpoint'] = {'num': num, 'id': id}
    MODEL.get_value('config')['Database'] = {'url': url, 'email': email, 'password': password}

    with open('config.ini', 'w') as configfile:
        MODEL.get_value('config').write(configfile)
        return render_template('index.html',config=request.form, error = error)

def main():
    config_server.run(debug=False, host='0.0.0.0', port=5000)
