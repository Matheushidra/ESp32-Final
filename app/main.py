from aiohttp import web
import json
import pathlib

# Diretório base do projeto
BASE_DIR = pathlib.Path(__file__).parent.parent

# Variável global que guarda o último comando
comando_atual = None

# Rota POST que recebe o comando do botão
async def receber_comando(request):
    global comando_atual
    dados = await request.json()
    comando_atual = dados.get('comando')
    return web.Response(text="Comando recebido")

# Rota GET que o ESP32 consulta para saber o comando atual
async def status(request):
    return web.json_response({"comando": comando_atual})

# Cria o aplicativo e define as rotas
app = web.Application()
app.router.add_post('/api/comando', receber_comando)
app.router.add_get('/api/status', status)

# Corrige o caminho da pasta 'public' para funcionar na Render
app.router.add_static('/', path=str(BASE_DIR / 'public'), name='static')

# Inicia o servidor
web.run_app(app, host='0.0.0.0', port=8080)
