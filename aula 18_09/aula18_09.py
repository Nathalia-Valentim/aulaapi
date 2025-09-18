from flask import Flask, request
import mysql.connector

app = Flask(__name__)

def conectar():
    conn = mysql.connector.connect(host='localhost', username='root', password='fiap', database='faculdade')
    cursor = conn.cursor(dictionary=True)

    return conn, cursor

@app.route('/bom_dia', methods=['POST'])
def cumprimentar():
    conectar()

    nome = request.args.get('nome')

    query = 'SELECT * FROM alunos WHERE nome = %s'
    cursor.execute(query, (nome, ))
    aluno = cursor.fetchone()

    return aluno

app.run(debug=True)