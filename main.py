from flask import Flask, render_template, request
import requests
import sqlite3
import logging
from audio_notification import notificar_audio 
from datetime import datetime
 

app = Flask(__name__)

class AgenteMudancasClimaticas:
    def __init__(self, api_key):
        self.api_key = api_key
        self.conn = self.criar_conexao_db()
        self.cidade = "Maputo"  # Cidade padrão

    def criar_conexao_db(self):
        try:
            conn = sqlite3.connect('clima_dados.db')
            logging.info("Conexão com o banco de dados estabelecida.")
            return conn
        except sqlite3.Error as e:
            logging.error(f"Erro ao conectar ao banco de dados: {e}")
            return None

    def obter_dados_clima(self, cidade):
        base_url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={self.api_key}&units=metric&lang=pt"
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Erro ao obter dados da API: {e}")
            return None

    def obter_dados_previsao(self, cidade):
        base_url = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={self.api_key}&units=metric&lang=pt"
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Erro ao obter dados da API: {e}")
            return None

    def obter_clima_atual(self, cidade):
        dados = self.obter_dados_clima(cidade)
        if dados and 'main' in dados:
            return {
                'temperatura': dados['main']['temp'],
                'umidade': dados['main']['humidity'],
                'descricao': dados['weather'][0]['description']
            }
        return None

    def obter_previsao_5_dias(self, cidade):
        dados = self.obter_dados_previsao(cidade)
        previsao = []
        if dados and 'list' in dados:
            for item in dados['list']:
                previsao.append({
                    'data': item['dt_txt'],
                    'temperatura': item['main']['temp'],
                    'descricao': item['weather'][0]['description']
                })
        return previsao
    
    

def criar_tabelas():
    conn = sqlite3.connect('comunidade.db')
    cursor = conn.cursor()
    
    # Criar tabela para postagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            titulo TEXT,
            conteudo TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar tabela para comentários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            usuario TEXT,
            conteudo TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')
    
    conn.commit()
    conn.close()

criar_tabelas()


# Definir o filtro datetimeformat globalmente
@app.template_filter('datetimeformat')
def datetimeformat(value):
    return datetime.fromtimestamp(value).strftime('%d/%m/%Y %H:%M') if value else 'Data inválida'

# Rota da página inicial
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clima', methods=['GET', 'POST'])
def clima():
    api_key = "8edd0e4319e7623092d5927f85d972b7"  # Substitua pela sua chave da API
    agente = AgenteMudancasClimaticas(api_key)

    cidades_mocambique = ["Maputo", "Xai-Xai", "Beira", "Nampula", "Tete", "Chimoio", "Pemba"]

    if request.method == 'POST':
        cidade_selecionada = request.form['cidade']
        clima_info = agente.obter_clima_atual(cidade_selecionada)
        previsao_info = agente.obter_previsao_5_dias(cidade_selecionada)
        return render_template('clima.html', cidades=cidades_mocambique, clima_info=clima_info, cidade=cidade_selecionada, previsao=previsao_info)

    return render_template('clima.html', cidades=cidades_mocambique, clima_info=None)


@app.route('/dicas')
def dicas_sustentaveis():
    return render_template('dicas.html')


@app.route('/community', methods=['GET', 'POST'])
def comunidade():
    conn = sqlite3.connect('comunidade.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        usuario = request.form.get('usuario')
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')

        # Inserir nova postagem no banco de dados
        cursor.execute('''
            INSERT INTO posts (usuario, titulo, conteudo)
            VALUES (?, ?, ?)
        ''', (usuario, titulo, conteudo))
        conn.commit()

    # Obter todas as postagens
    cursor.execute('SELECT id, usuario, titulo, conteudo, data_criacao FROM posts ORDER BY data_criacao DESC')
    posts = cursor.fetchall()
    
    conn.close()
    return render_template('community.html', posts=posts)

@app.route('/comentarios/<int:post_id>', methods=['GET', 'POST'])
def comentarios(post_id):
    conn = sqlite3.connect('comunidade.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        usuario = request.form.get('usuario')
        conteudo = request.form.get('conteudo')

        # Inserir novo comentário
        cursor.execute('''
            INSERT INTO comentarios (post_id, usuario, conteudo)
            VALUES (?, ?, ?)
        ''', (post_id, usuario, conteudo))
        conn.commit()

    # Obter os detalhes da postagem
    cursor.execute('SELECT id, usuario, titulo, conteudo, data_criacao FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()

    # Obter todos os comentários para a postagem
    cursor.execute('SELECT usuario, conteudo, data_criacao FROM comentarios WHERE post_id = ? ORDER BY data_criacao DESC', (post_id,))
    comentarios = cursor.fetchall()
    
    conn.close()
    return render_template('comentarios.html', post=post, comentarios=comentarios)


@app.route('/artigos-tematicos')
def artigos_tematicos():
    return render_template('artigos_tematicos.html')

@app.route('/receitas-sustentaveis')
def receitas_sustentaveis():
    return render_template('receitas_sustentaveis.html')

@app.route('/artigos-educativos')
def artigos_educativos():
    return render_template('artigos_educativos.html')

@app.route('/videos-informativos')
def videos_informativos():
    return render_template('videos_informativos.html')

@app.route('/webinars-palestras')
def webinars_palestras():
    return render_template('webinars_palestras.html')

@app.route('/dicas-diarias')
def dicas_diarias():
    return render_template('dicas_diarias.html')




@app.route('/notificacoes', methods=['GET', 'POST'])
def notificacoes():
    api_key = "8edd0e4319e7623092d5927f85d972b7"
    agente = AgenteMudancasClimaticas(api_key)

    # Lista de cidades em Moçambique
    cidades_mocambique = ["Maputo", "Xai-Xai", "Beira", "Nampula", "Tete", "Chimoio", "Pemba"]

    cidade = "Maputo"  # Cidade padrão

    # Se o método for POST, obtenha a cidade selecionada pelo usuário
    if request.method == 'POST':
        cidade = request.form.get('cidade')

    # Obter o clima atual e a previsão para a cidade selecionada
    clima_atual = agente.obter_clima_atual(cidade)
    previsao = agente.obter_previsao_5_dias(cidade)

    alerts = []

    if clima_atual:
        temperatura_atual = clima_atual['temperatura']
        descricao_atual = clima_atual['descricao']

        if temperatura_atual >= 35:
            alerta = f"A temperatura atual em {cidade} é de {temperatura_atual}°C com {descricao_atual}. Muito quente! Hidrate-se e evite exposição prolongada ao sol."
        elif temperatura_atual <= 10:
            alerta = f"A temperatura atual em {cidade} é de {temperatura_atual}°C com {descricao_atual}. Está muito frio! Vista roupas quentes."
        else:
            alerta = f"A temperatura atual em {cidade} é de {temperatura_atual}°C com {descricao_atual}. O clima está agradável, aproveite o seu dia!"
        
        alerts.append(alerta)
        notificar_audio(alerta)  # Converte o alerta em áudio

    if previsao:
        for item in previsao:
            temp = item['temperatura']
            descricao = item['descricao']
            data_hora = item['data']

            if temp >= 35:
                alerta = f"Em {data_hora}: Temperatura prevista de {temp}°C com {descricao}. Prepare-se para um dia muito quente! Use protetor solar e hidrate-se bem."
            elif temp <= 10:
                alerta = f"Em {data_hora}: Temperatura prevista de {temp}°C com {descricao}. Vista roupas quentes, pois estará muito frio."
            else:
                alerta = f"Em {data_hora}: Temperatura prevista de {temp}°C com {descricao}. O clima estará agradável."
            
            alerts.append(alerta)
            notificar_audio(alerta)  # Converte o alerta em áudio

    return render_template('notificacoes.html', alerts=alerts, cidades=cidades_mocambique, cidade_selecionada=cidade)

 
if __name__ == '__main__':
    app.run(debug=True)
