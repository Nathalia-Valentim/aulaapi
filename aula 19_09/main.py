from flask import Flask, render_template

app = Flask(__name__)

@app.route('/ola')
def home():
    return render_template('index19_09.html')

app.run(debug=True, port=8080)