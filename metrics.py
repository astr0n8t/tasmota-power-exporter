import requests
import os
from dotenv import load_dotenv
from flask import Flask
app = Flask(__name__)

load_dotenv()
ip = os.getenv('DEVICE_IP')
user = os.getenv('USER')
password = os.getenv('PASSWORD')

def get_values():

    url = 'http://' + ip + '/?m=1'

    session = requests.Session()
    
    if user and password:
        session.auth = (user, password)

    page = session.get(url)

    values = {}

    string_values = str(page.text).split("{s}")
    for i in range(1,len(string_values)-1):
        label = string_values[i].split("{m}")[0]
        value = string_values[i].split("{m}")[1].split("{e}")[0]
        values[label] = value

    return values

@app.route('/metrics')
def return_metrics():

    response = ""

    data = get_values()

    for key in data:
        line = key.lower().replace(" ", "_") + " " + data[key].split()[0] + '\n'
        response += line

    return(response)
