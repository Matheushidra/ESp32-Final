import os
import json
from aiohttp import web

# IP fixo que o ESP32 terá na sua rede local
ESP32_IP = os.environ.get("ESP32_IP", "192.168.1.50")

routes = web.RouteTableDef()
clientes = []

@routes.get('/')
async def index(request):
    return web.FileResponse(path='public/index.html')

@routes.get('/ws')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # identifica pelo IP
    client_ip = request.remote
    tipo = 'esp32' if client_ip == ESP32_IP else 'site'
    clientes.append({'ws': ws, 'tipo': tipo})
    print(f"Cliente conectado: {client_ip} → {tipo}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                comando = msg.data.strip()
                print(f"Recebido de {tipo}: {comando}")

                # só repassa para ESP32
                if tipo == 'site':
                    for c in clientes:
                        if c['tipo'] == 'esp32' and not c['ws'].closed:
                            await c['ws'].send_str(comando)

            elif msg.type == web.WSMsgType.ERROR:
                print(f"Erro WebSocket ({client_ip}): {ws.exception()}")
    finally:
        clientes[:] = [c for c in clientes if c['ws'] is not ws]
        print(f"Cliente desconectado: {client_ip}")

    return ws

app = web.Application()
app.add_routes(routes)
app.router.add_static('/', path='public', name='static')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"Iniciando servidor na porta {port}, ESP32_IP={ESP32_IP}")
    web.run_app(app, port=port)
