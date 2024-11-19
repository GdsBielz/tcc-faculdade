from datetime import datetime
from decimal import Decimal
from functools import wraps
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from libs.sql import sqlExecute, sqlSelectDict

page = Blueprint('page', __name__)

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin'):
            return redirect(url_for('auth.login'))  # Redireciona para a página de login
        return func(*args, **kwargs)
    return decorated_function

def getUsername(completo=False):
    nomeUsuario = session['user_nome']
    if nomeUsuario is not None:
        if completo:
            return nomeUsuario
        else:
            partesNome = nomeUsuario.split(" ")

            if len(partesNome) >= 2:
                nomeUsuario = partesNome[0]
                return nomeUsuario
            else:
                # Se não houver sobrenome, retorna o nome completo
                return nomeUsuario
    else:
        return "Usuário"

@page.route("/")
def raiz():
    logado = session.get("loggedin")
    return redirect("/home") if logado else redirect("/landing-page")
        

@page.route("/home")
@login_required
def home():
    nomeUsuario = getUsername()
    usuario_id = session.get('user_id')
    
    # Buscar dados do banco
    dados = sqlSelectDict("SELECT * FROM dadosmotoristas WHERE usuario_id = %s ORDER BY dataHora DESC", (usuario_id,))
    
    # Processar os dados
    ultimos_lancamentos = []
    historico_km = []
    ultima_corrida = None
    saldo_atual = 0  # Valor inicial do saldo (ajuste conforme necessário)

    for dado in dados:
        tipoDado = dado['tipoDado']
        valor = float(dado['valor'])  # Garantir que o valor seja numérico
        dataHora = dado['dataHora']
        manutencao = dado.get('manutencao')
        litros = dado.get('litros')
        km = dado.get('km')


        if tipoDado == "corrida":
            # Última corrida
            if not ultima_corrida:
                ultima_corrida = datetime.strptime(dataHora, "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y - %H:%M")
            saldo_atual += valor
            if km:
                historico_km.append({"km": km, "valor": valor})
            
            cor = 'green'

        elif tipoDado == "abastecimento":
            saldo_atual -= valor
            cor = 'red'
        elif tipoDado == "manutencao":
            saldo_atual -= valor
            cor = 'red'

        if saldo_atual < 0:
            situacao_atual = {
                "mensagem": "Você precisa melhorar!",
                "cor": "red"
            }
        else:
            situacao_atual = {
                "mensagem": "Você está indo bem!",
                "cor": "green"
            }
        # Adicionar ao histórico de lançamentos
        servico = tipoDado.capitalize() if not manutencao else manutencao
        forma_pagamento = "Não especificado"  # Ajustar caso tenha outra coluna
        ultimos_lancamentos.append({
            "servico": servico,
            "pagamento": forma_pagamento,
            "valor": valor,
            "cor": cor
        })

    # Limitar itens a exibir (se necessário)
    ultimos_lancamentos = ultimos_lancamentos[:4]
    historico_km = historico_km[:5]
    saldo_atual = f"{saldo_atual:,.2f}"

    return render_template(
        "home.html",
        nomeUsuario=nomeUsuario,
        ultimos_lancamentos=ultimos_lancamentos,
        historico_km=historico_km,
        ultima_corrida=ultima_corrida,
        saldo_atual=saldo_atual,
        situacao_atual=situacao_atual
    )


@page.route("/caixa")
@login_required
def caixa():
    nomeUsuario = getUsername()
    return render_template("caixa.html", nomeUsuario=nomeUsuario)

@page.route("/metas")
@login_required
def metas():
    nomeUsuario = getUsername()
    usuario_id = session.get('user_id')
    metas = sqlSelectDict("SELECT * FROM metas WHERE usuario_id = %s", (usuario_id,))
    
    total_metas = len(metas)
    metas_concluidas = sum(1 for meta in metas if meta['concluida'])
    porcentagem_concluidas = round((metas_concluidas / total_metas * 100), 2) if total_metas > 0 else 0


    return render_template('metas.html', metas=metas, porcentagem=porcentagem_concluidas, nomeUsuario=nomeUsuario)

@page.route('/add-meta', methods=['POST'])
@login_required
def add_meta():
    descricao = request.form.get('descricao')
    usuario_id = session.get('user_id')
    
    if descricao:
        sqlExecute("INSERT INTO metas (descricao, usuario_id, concluida) VALUES (%s, %s, %s)", (descricao, usuario_id, 0))
    return redirect(url_for('page.metas'))

@page.route('/update-meta/<int:id>', methods=['POST'])
@login_required
def update_meta(id):
    usuario_id = session.get('user_id')
    meta = sqlSelectDict("SELECT * FROM metas WHERE idmeta = %s AND usuario_id = %s", (id, usuario_id))
    
    if meta:
        concluida = meta[0]['concluida']
        if concluida == 0:
            concluida = 1
        else:
            concluida = 0
        sqlExecute("UPDATE metas SET concluida = %s WHERE idmeta = %s AND usuario_id = %s", (concluida, id, usuario_id))
    return redirect(url_for('page.metas'))

@page.route('/delete-meta/<int:id>', methods=['POST'])
@login_required
def delete_meta(id):
    usuario_id = session.get('user_id')
    sqlExecute("DELETE FROM metas WHERE idmeta = %s AND usuario_id = %s", (id, usuario_id))
    return redirect(url_for('page.metas'))

@page.route("/dashboard")
@login_required
def dashboard():
    nomeUsuario = getUsername()
    usuario_id = session.get('user_id')

    # Buscar dados do banco
    dados = sqlSelectDict("SELECT * FROM dadosmotoristas WHERE usuario_id = %s ORDER BY dataHora DESC", (usuario_id,))
    
    total_ganhos_bruto = Decimal(0)
    total_ganhos_liquido = Decimal(0)
    total_gastos = Decimal(0)
    
    # Inicializando os totais das categorias de gráfico
    corridas_mensais = [0] * 12  # Para armazenar o total de corridas por mês
    categoria_valores = {"abastecimento": 0, "corrida": 0, "manutencao": 0}
    
    # Loop para calcular totais
    for dado in dados:
        tipoDado = dado['tipoDado']
        valor = Decimal(dado['valor'])
        dataHora = dado['dataHora']
        
        # Verificar se a dataHora não é None antes de tentar processar
        if dataHora:
            mes = int(dataHora.split('-')[1]) - 1  # Extrair o mês da data (0 = Janeiro, 11 = Dezembro)
        else:
            mes = -1  # Caso não haja data válida, ignore esse dado

        if tipoDado == 'corrida':
            total_ganhos_bruto += valor  # Corridas geram ganhos brutos
            total_ganhos_liquido += valor  # Podemos somar ao valor líquido aqui, caso não haja deduções
            if mes != -1:
                corridas_mensais[mes] += 1  # Contabiliza a corrida no mês
                
        elif tipoDado in categoria_valores:
            categoria_valores[tipoDado] += valor  # Abastecimento e manutenção são gastos
    
    # Formatando os valores
    total_ganhos_bruto_formatado = f"R$ {total_ganhos_bruto:,.2f}"
    total_ganhos_liquido_formatado = f"R$ {total_ganhos_liquido:,.2f}"
    total_gastos_formatado = f"R$ {total_gastos:,.2f}"

    # Passando os dados para o template
    return render_template(
        "dashboard.html",
        nomeUsuario=nomeUsuario,
        total_ganhos_bruto=total_ganhos_bruto_formatado,
        total_ganhos_liquido=total_ganhos_liquido_formatado,
        total_gastos=total_gastos_formatado,
        corridas_mensais=corridas_mensais,
        categoria_valores=categoria_valores
    )



@page.route("/insercao")
@login_required
def insercao():
    nomeUsuario = getUsername()
    return render_template("insercao.html", nomeUsuario=nomeUsuario)

@page.route("/api/insercao", methods=["POST"])
@login_required
def api_insercao():
    try:

        data = request.get_json()
        usuario_id = session.get('user_id')
        tipo = data["tipo"]

        # Inicializar campos opcionais como None
        km = data.get("km")
        litros = data.get("litros")
        nome = data.get("nome")
        valor = data.get("valor") or data.get("valorTotal")

        # Determinar os campos e valores dinamicamente
        campos = ["usuario_id", "tipoDado", "valor"]
        valores = [usuario_id, tipo, valor]

        if km is not None:
            campos.append("km")
            valores.append(km)
        elif litros is not None:
            campos.append("litros")
            valores.append(litros)
        elif nome is not None:
            campos.append("manutencao")
            valores.append(nome)

        # Gerar a query dinâmica
        query = f"""INSERT INTO dadosmotoristas ({', '.join(campos)}, dataHora) 
                    VALUES ({', '.join(['%s'] * len(valores))}, NOW())"""

        # Executar a query
        sqlExecute(query, tuple(valores))


        # Retorna uma resposta de sucesso
        return jsonify({"message": "Registro inserido com sucesso!"}), 200
    except Exception as e:
        print("Erro ao processar os dados:", e)
        return jsonify({"error": "Ocorreu um erro ao processar os dados."}), 500
    
@page.route("/conta")
@login_required
def conta():
    nomeUsuario = getUsername(completo=True)
    emailUsuario = session.get("user_email")
    return render_template("conta.html", nomeUsuario=nomeUsuario, emailUsuario = emailUsuario)

@page.route("/configuracoes")
@login_required
def configuracoes():
    nomeUsuario = getUsername(completo=True)
    return render_template("configuracoes.html", nomeUsuario=nomeUsuario)

@page.route("/landing-page")
def landingPage():
    return render_template("landingPage.html")