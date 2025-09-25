from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/cumprimentar')
def cumprimentar():
    nome = request.args.get('nome')
    return render_template('cumprimentar.html', nome_usuario=nome)

@app.route('/string')
def comprimento_string():
    return render_template('string.html')

@app.route('/soma')
def soma():
    return render_template('soma.html')

@app.route('/divisao')
def divisao():
    return render_template('divisao.html')

app.run(debug=True, port=8080)