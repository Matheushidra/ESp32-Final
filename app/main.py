import asyncio
from aiohttp import web
import os
import json

routes = web.RouteTableDef()
clientes = []

@routes.get('/')
async def index(request):
    return web.FileResponse(path='public/index.html')

@routes.get('/ws')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    cliente = {'ws': ws, 'tipo': None}
    clientes.append(cliente)
    print("Cliente conectado.")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)

                    # Identificação
                    if 'identidade' in data:
                        cliente['tipo'] = data['identidade']
                        print(f"Cliente se identificou como: {cliente['tipo']}")
                        continue

                    # Se é comando do site, envia só ao ESP32
                    if cliente['tipo'] == 'site' and 'comando' in data:
                        print(f"Comando do site: {data['comando']}")
                        for c in clientes:
                            if c['tipo'] == 'esp32' and not c['ws'].closed:
                                await c['ws'].send_str(data['comando'])

                except json.JSONDecodeError:
                    print("Mensagem inválida.")
            elif msg.type == web.WSMsgType.ERROR:
                print(f"Erro WebSocket: {ws.exception()}")
    finally:
        clientes.remove(cliente)
        print("Cliente desconectado.")
    return ws

app = web.Application()
app.add_routes(routes)
app.router.add_static('/', path='public', name='static')

if __name__ == '__main__':
    web.run_app(app, port=int(os.environ.get("PORT", 10000)))
