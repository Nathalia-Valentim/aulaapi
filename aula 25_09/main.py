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
    uma_string_qualquer = request.args.get('q')
    comprimento = None
    if uma_string_qualquer:
        comprimento = len(uma_string_qualquer)
    
    return render_template('string.html', x = comprimento)

@app.route('/soma')
def soma():
    a = request.args.get('a')
    b = request.args.get('b')
    resultado = None
    erro = None

    if a is not None and b is not None:
        try:
            soma_val = float(a) + float(b)
            # mostra inteiro se não tiver parte decimal
            if soma_val.is_integer():
                soma_val = int(soma_val)
            resultado = soma_val
        except ValueError:
            erro = "Digite números válidos."

    return render_template('soma.html', resultado=resultado, erro=erro, a=a, b=b)

@app.route('/divisao')
def divisao():
    a = request.args.get('a')
    b = request.args.get('b')
    resultado = None
    erro = None

    if a is not None and b is not None:
        try:
            num = float(a)
            den = float(b)
            if den == 0:
                erro = "Erro: divisão por zero não permitida."
            else:
                div_val = num / den
                if div_val.is_integer():
                    div_val = int(div_val)
                resultado = div_val
        except ValueError:
            erro = "Digite números válidos."

    return render_template('divisao.html', resultado=resultado, erro=erro, a=a, b=b)

if __name__ == '__main__':
    app.run(debug=True, port=8080)