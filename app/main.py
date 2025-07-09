from aiohttp import web
import json

comando_atual = None

async def receber_comando(request):
    global comando_atual
    dados = await request.json()
    comando_atual = dados.get('comando')
    return web.Response(text="Comando recebido")

async def status(request):
    return web.json_response({"comando": comando_atual})

app = web.Application()
app.router.add_post('/api/comando', receber_comando)
app.router.add_get('/api/status', status)
app.router.add_static('/', path='public', name='static')

web.run_app(app, host="0.0.0.0", port=8080)
