from flask import Flask, jsonify, render_template
import web3calls
import genGraphs
from waitress import serve
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update')
def update():
    data = jsonify(web3calls.getWeb3Data())
    return data

if __name__ == '__main__':
    # check whether static/chart.gif exists:
    # if not, create it:
    if not os.path.exists('static/chart.gif'):
        genGraphs.createPlots()
    
    # run app:
    print("app deployed at: 192.168.1.73:5001")
    serve(app, host='0.0.0.0', port=5001)