from flask import Flask, request, jsonify
import os
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)

products = []
next_id = 1

# ----------- Nível 1: básico -----------

# 1. Crie uma rota / que retorne a string "Bem-vindo à minha API!".
@app.route("/")
def diga_ola():
    return "Bem-vindo à minha API!"

#2. Crie uma rota /info que retorne um objeto JSON: {"versao": "1.0", "autor": "Seu Nome"}.
@app.route("/info")
def info():
    return {
        "versao": "1.0",
        "autor": "Nathalia"
    }

# 3. Crie uma rota dinâmica /user/<username> que capture o nome do usuário e retorne um JSON de boas-vindas, como: {"message": "Olá, [username]!"}.
@app.route("/user/<username>")
def user(username):
    return {"message":f"Olá, {username}!"}

# 4. Crie uma rota /soma/<int:num1>/<int:num2> que receba dois números inteiros e retorne a soma deles em um JSON.
@app.route("/soma/<int:num1>/<int:num2>")
def soma(num1, num2):
    return {
        "resultado": num1 + num2
    }

# 5. Crie uma rota /posts que aceite apenas o método POST e retorne um JSON {"status": "Post recebido com sucesso"}.
@app.route("/posts", methods=["POST"])
def posts():
    return {
        "status": "Post recebido com sucesso"
    }

# ----------- Nível 2: intermediário (CRUD em memória) -----------

# 6. Crie uma rota /search que receba um parâmetro de consulta (query string) q (ex: /search?q=python) e retorne {"buscando_por": "python"}.
@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q")
    return jsonify({"buscando_por": q})

# 7. Crie um endpoint POST /products. Ele deve receber um corpo JSON com name e price, adicionar a uma lista em memória e retornar o produto adicionado com um id.
@app.route("/products", methods=["POST"])
def create_product():
    global next_id
    data = request.get_json()

    product = {
        "id": next_id,
        "name": data["name"],
        "price": data["price"]
    }
    products.append(product)
    next_id += 1

    return 'Okk'

# 8. Crie um endpoint GET /products que retorne a lista completa de produtos cadastrados em memória.
@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)

# 9. Crie um endpoint PUT /products/<int:product_id> que atualize um produto na lista em memória com base nos dados recebidos no corpo da requisição.
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()
    for product in products:
        if product["id"] == product_id:
            product["name"] = data.get("name", product["name"])
            product["price"] = data.get("price", product["price"])
            return jsonify(product)
    return jsonify({"error": "Produto não encontrado"}), 404

# 10. Crie um endpoint DELETE /products/<int:product_id> que remova um produto da lista em memória.
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    global products
    products = [product for product in products if product["id"] != product_id]
    return jsonify({"status": "Produto removido com sucesso"})

# ----------- Nível 3: integração com MySQL -----------

# 11. (Setup) Crie uma tabela authors (id, name, country). Crie um endpoint POST /authors que insere um novo autor no banco de dados.
@app.route('/authors', methods=['POST'])
def create_author():
    conn = mysql.connector.connect(host='127.0.0.1', username='root', password='Fiap563503', database='banco_authors')
    cursor = conn.cursor()
    
    data = request.get_json()
    name = data.get('name')
    country = data.get('country')
    
    query = 'INSERT INTO authors (name, country) VALUES (%s, %s)'
    
    cursor.execute(query, (name, country))
    conn.commit()
    
    return 'Usuário cadastrado com sucesso'

# 12. Crie um endpoint GET /authors que busca e retorna todos os autores do banco de dados MySQL.
@app.route('/authors', methods=['GET'])
def get_authors():
    conn = mysql.connector.connect(host='localhost', username='root', password='', database='banco_authors')
    cursor = conn.cursor(dictionary=True)
    
    query = 'SELECT * FROM authors'
    
    cursor.execute(query)
    
    authors = cursor.fetchall()
    
    return authors

# 13. Crie um endpoint GET /authors/<int:author_id> que busca e retorna um autor específico pelo seu ID.
@app.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    conn = mysql.connector.connect(host='localhost', username='root', password='', database='banco_authors')
    cursor = conn.cursor(dictionary=True)
    
    query = 'SELECT * FROM authors WHERE id = %s'
    
    cursor.execute(query, (author_id,))
    
    author = cursor.fetchone()
    
    if author:
        return author
    else:
        return {'erro': 'Autor não encontrado'}, 404

# 14. Crie um endpoint PUT /authors/<int:author_id> que atualiza as informações de um autor no banco de dados.
@app.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):   
    conn = mysql.connector.connect(host='localhost', username='root', password='', database='banco_authors')
    cursor = conn.cursor()
    
    data = request.get_json()
    name = data.get('name')
    country = data.get('country')
    
    query = 'UPDATE authors SET name = %s, country = %s WHERE id = %s'
    
    cursor.execute(query, (name, country, author_id))
    conn.commit()
    
    return jsonify({"id": author_id, "name": name, "country": country})

# 15. Crie um endpoint DELETE /authors/<int:author_id> que remove um autor do banco de dados.
@app.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    conn = mysql.connector.connect(host='localhost', username='root', password='', database='banco_authors')
    cursor = conn.cursor()
    
    query = 'DELETE FROM authors WHERE id = %s'
    
    cursor.execute(query, (author_id,))
    conn.commit()
    
    return jsonify({"status": "Autor removido com sucesso"})


# ----------- Executar API -----------
if __name__ == "__main__":
    app.run(port=8080, debug=True)
