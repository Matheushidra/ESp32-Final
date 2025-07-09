import asyncio
from aiohttp import web
import os

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse(path='public/index.html')

@routes.get('/ws')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            print(f"Mensagem recebida: {msg.data}")
            await ws.send_str(f"Comando recebido: {msg.data}")
        elif msg.type == web.WSMsgType.ERROR:
            print(f"Erro na conexão WebSocket: {ws.exception()}")

    print("WebSocket fechado")
    return ws

app = web.Application()
app.add_routes(routes)

# Definindo o diretório público para arquivos estáticos (JS, CSS, etc)
app.router.add_static('/static/', path='public', name='static')

if __name__ == '__main__':
    web.run_app(app, port=int(os.environ.get('PORT', 10000)))

