import asyncio
from aiohttp import web
import os

routes = web.RouteTableDef()
clients = set()

@routes.get('/')
async def index(request):
    return web.FileResponse(path='public/index.html')

@routes.get('/ws')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)
    print("Novo cliente conectado!")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                print(f"Mensagem recebida: {msg.data}")
                # Enviar para todos os clientes conectados
                for client in clients:
                    if not client.closed:
                        await client.send_str(msg.data)
            elif msg.type == web.WSMsgType.ERROR:
                print(f"Erro na conexão WebSocket: {ws.exception()}")
    finally:
        clients.remove(ws)
        print("Cliente desconectado.")

    return ws

app = web.Application()
app.add_routes(routes)
app.router.add_static('/static/', path='public', name='static')

if __name__ == '__main__':
    web.run_app(app, port=10000)
