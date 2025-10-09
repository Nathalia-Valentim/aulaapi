from flask import Flask, request, jsonify
import mysql.connector
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# ---------- CONFIGURAÇÃO SIMPLES (ajuste conforme seu ambiente) ----------
# MySQL (preencha sua senha / host / database)
MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "user": "root",
    "password": "fiap",       # <-- coloque sua senha aqui
    "database": "banco_authors"  # <-- crie esse DB / tabela authors (veja SQL abaixo)
}

# MongoDB (assume mongodb rodando local)
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "my_db"
MONGO_COLLECTION = "books"

# ---------- Conexão Mongo (simples singleton) ----------
mongo = MongoClient(MONGO_URI)
books_col = mongo[MONGO_DB][MONGO_COLLECTION]

# ---------- Memória (Nível 2) ----------
products = []
_next_product_id = 1

# ---------- NÍVEL 1: Básico ----------
@app.route("/", methods=["GET"])
def rota_raiz():
    return "Bem-vindo à minha API!"

@app.route("/info", methods=["GET"])
def rota_info():
    return jsonify({"versao": "1.0", "autor": "Seu Nome"})

@app.route("/user/<username>", methods=["GET"])
def rota_user(username):
    return jsonify({"message": f"Olá, {username}!"})

@app.route("/soma/<int:num1>/<int:num2>", methods=["GET"])
def rota_soma(num1, num2):
    return jsonify({"resultado": num1 + num2})

@app.route("/posts", methods=["POST"])
def rota_posts():
    return jsonify({"status": "Post recebido com sucesso"})

# ---------- NÍVEL 2: CRUD em Memória ----------
@app.route("/search", methods=["GET"])
def rota_search():
    q = request.args.get("q", "")
    return jsonify({"buscando_por": q})

@app.route("/products", methods=["POST"])
def create_product():
    global _next_product_id
    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    if not name or price is None:
        return jsonify({"error": "name e price são obrigatórios"}), 400
    try:
        price = float(price)
    except ValueError:
        return jsonify({"error": "price deve ser numérico"}), 400
    product = {"id": _next_product_id, "name": name, "price": price}
    products.append(product)
    _next_product_id += 1
    return jsonify(product), 201

@app.route("/products", methods=["GET"])
def list_products():
    return jsonify(products)

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json() or {}
    for p in products:
        if p["id"] == product_id:
            if "name" in data:
                p["name"] = data["name"]
            if "price" in data:
                try:
                    p["price"] = float(data["price"])
                except ValueError:
                    return jsonify({"error": "price deve ser numérico"}), 400
            return jsonify(p)
    return jsonify({"error": "Produto não encontrado"}), 404

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    global products
    new = [p for p in products if p["id"] != product_id]
    if len(new) == len(products):
        return jsonify({"error": "Produto não encontrado"}), 404
    products = new
    return jsonify({"status": "Produto removido com sucesso"})

# ---------- NÍVEL 3: MySQL (authors) ----------
# SQL para criar tabela authors (execute no seu MySQL):
# CREATE DATABASE banco_authors;
# USE banco_authors;
# CREATE TABLE authors (
#   id INT AUTO_INCREMENT PRIMARY KEY,
#   name VARCHAR(255) NOT NULL,
#   country VARCHAR(255)
# );

def mysql_conn():
    return mysql.connector.connect(**MYSQL_CONFIG)

@app.route("/authors", methods=["POST"])
def create_author():
    data = request.get_json() or {}
    name = data.get("name")
    country = data.get("country", "")
    if not name:
        return jsonify({"error": "name é obrigatório"}), 400
    conn = mysql_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO authors (name, country) VALUES (%s, %s)", (name, country))
    conn.commit()
    author_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"id": author_id, "name": name, "country": country}), 201

@app.route("/authors", methods=["GET"])
def get_authors():
    conn = mysql_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM authors")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route("/authors/<int:author_id>", methods=["GET"])
def get_author(author_id):
    conn = mysql_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM authors WHERE id = %s", (author_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Autor não encontrado"}), 404

@app.route("/authors/<int:author_id>", methods=["PUT"])
def update_author(author_id):
    data = request.get_json() or {}
    name = data.get("name")
    country = data.get("country")
    if name is None and country is None:
        return jsonify({"error": "envie name ou country"}), 400
    conn = mysql_conn()
    cur = conn.cursor()
    # atualiza somente o que foi enviado
    sets, params = [], []
    if name is not None:
        sets.append("name=%s"); params.append(name)
    if country is not None:
        sets.append("country=%s"); params.append(country)
    params.append(author_id)
    cur.execute(f"UPDATE authors SET {', '.join(sets)} WHERE id = %s", tuple(params))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": author_id, "name": name, "country": country})

@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    conn = mysql_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM authors WHERE id = %s", (author_id,))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    if affected == 0:
        return jsonify({"error": "Autor não encontrado"}), 404
    return jsonify({"status": "Autor removido com sucesso"})

# ---------- NÍVEL 4: MongoDB (books) ----------
def serialize_book(doc):
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "author": doc.get("author"),
        "year": doc.get("year"),
        "tags": doc.get("tags", [])
    }

@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json() or {}
    title = data.get("title"); author = data.get("author")
    year = data.get("year"); tags = data.get("tags", [])
    if not title or not author:
        return jsonify({"error": "title e author são obrigatórios"}), 400
    doc = {"title": title, "author": author, "year": year, "tags": tags}
    res = books_col.insert_one(doc)
    doc["_id"] = res.inserted_id
    return jsonify(serialize_book(doc)), 201

@app.route("/books", methods=["GET"])
def get_books():
    docs = list(books_col.find())
    return jsonify([serialize_book(d) for d in docs])

@app.route("/books/search", methods=["GET"])
def search_books():
    author_q = request.args.get("author")
    query = {}
    if author_q:
        query["author"] = author_q
    docs = list(books_col.find(query))
    return jsonify([serialize_book(d) for d in docs])

@app.route("/books/<book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json() or {}
    try:
        oid = ObjectId(book_id)
    except Exception:
        return jsonify({"error": "book_id inválido"}), 400
    update = {}
    for k in ("title", "author", "year", "tags"):
        if k in data:
            update[k] = data[k]
    if not update:
        return jsonify({"error": "nenhum campo para atualizar"}), 400
    res = books_col.update_one({"_id": oid}, {"$set": update})
    if res.matched_count == 0:
        return jsonify({"error": "Livro não encontrado"}), 404
    doc = books_col.find_one({"_id": oid})
    return jsonify(serialize_book(doc))

@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        oid = ObjectId(book_id)
    except Exception:
        return jsonify({"error": "book_id inválido"}), 400
    res = books_col.delete_one({"_id": oid})
    if res.deleted_count == 0:
        return jsonify({"error": "Livro não encontrado"}), 404
    return jsonify({"status": "Livro removido com sucesso"})

# ---------- RODAR API ----------
if __name__ == "__main__":
    app.run(port=8080, debug=True)
