import asyncio
from aiohttp import web

connected_clients = {}

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse(path='public/index.html')

@routes.get('/ws')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    esp_id = None

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            text = msg.data.strip()
            print(f"Mensagem recebida: {text}")

            if text == "esp32":
                esp_id = "esp32"
                connected_clients[esp_id] = ws
                print("ESP32 registrado com sucesso")
                await ws.send_str("Servidor reconheceu ESP32")

            elif text in ["ligar", "desligar"] and "esp32" in connected_clients:
                await connected_clients["esp32"].send_str(text)

        elif msg.type == web.WSMsgType.ERROR:
            print(f"Erro na conexão WebSocket: {ws.exception()}")

    if esp_id and esp_id in connected_clients:
        del connected_clients[esp_id]
        print(f"ESP32 desconectado")

    return ws

app = web.Application()
app.add_routes(routes)
app.router.add_static('/static/', path='public', name='static')

if __name__ == '__main__':
    web.run_app(app, port=10000)
