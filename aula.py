from flask import Flask, request # type: ignore

app = Flask(__name__)

@app.route('/')
def diga_ola():
    return 'Opa, beleza?'

@app.route('/search/<termo_pesquisa>')
def procura(termo_pesquisa):
    if termo_pesquisa == 'gato':
        return '<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRkZ8cd8Kc1yxRHTF_WISYtgeOtkFa2rrGzfA&s">'
    else:
        return f'Você está procurando pelo termo {termo_pesquisa}'

@app.route('/calculadora/<funcao>')
def calculadora(funcao):
    try:
        a = float(request.args.get('a'))
        b = float(request.args.get('b'))
    except:
        return 'Informe a e b', 400 

    if funcao == 'soma':
        return f'{a + b}'
    elif funcao == 'subtracao':
        return f'{a - b}'
    elif funcao == 'multiplicacao':
        return f'{a * b}'
    elif funcao == 'divisao':
        return f'{a // b}'

@app.route('/teste', methods=['POST'])
def teste():
    return 'teste com falha', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)