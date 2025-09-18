from flask import Flask, request # type: ignore
import mysql.connector

app = Flask(__name__)

@app.route('/cadastrar')
def cadastrar_usuario():
  conn = mysql.connector.connect(host='localhost', username='root', password='fiap', database='fiapbank')
  cursor = conn.cursor(dictionary=True)
  
  cpf = request.args.get('cpf')
  
  query = 'insert into saldo values (%s, %s)'
  
  cursor.execute(query, (cpf, 10))
  conn.commit()
  
  return 'Usuário cadastrado com sucesso'
  

@app.route('/meu_saldo')
def ler_saldo_usuario():
  conn = mysql.connector.connect(host='localhost', username='root', password='fiap', database='fiapbank')
  cursor = conn.cursor(dictionary=True)
  
  cpf = request.args.get('cpf')
  login = request.headers.get('login')
  senha = request.headers.get('senha')
  
  if login == 'elvis' and senha == 'fiap':
    query = 'SELECT * FROM saldo WHERE cpf = %s'
    
    cursor.execute(query, (cpf, ))
    
    resultado_bd = cursor.fetchone()
    
    if resultado_bd:
      return resultado_bd
    else:
      return {'erro': 'CPF não encontrado'}
  else:
    return {'erro': 'Usuário não autenticado'}

@app.route('/authors/<int:author_id>', methods=['PATCH'])
def register_author(author_id):
  
  dados = {
    'metodo': request.method,
    'url': request.url,
    'variaveis_do_path': {
      'author_id': author_id
    },
    'query_string': request.args,
    'cabecalhos_requisicao': dict(request.headers),
    'corpo_requisicao': request.get_json()
  }
  
  return dados, 200, {'header2': 'valor2'}

app.run(debug=True, port=8000)
 