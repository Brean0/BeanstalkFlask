from flask import Flask, jsonify, render_template
import web3calls
import genGraphs
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
        print("Creating chart.gif")
        genGraphs.createPlots()
    
    # run app:
    print("running app")
    # serve(app, host='0.0.0.0', port=5001)
    # run app with debug mode:
    # app.run(debug=True, port=5001)
