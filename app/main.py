import os
import json
from aiohttp import web

# IP fixo (ou variável de ambiente) do seu ESP32 na rede local
ESP32_IP = os.environ.get("ESP32_IP", "192.168.1.50")

routes = web.RouteTableDef()
clientes = []  # lista de dicts {'ws': WebSocketResponse, 'tipo': 'site'|'esp32', 'ip': '...'}

@routes.get('/')
async def index(request):
    return web.FileResponse(path='public/index.html')

@routes.get('/ws')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    client_ip = request.remote
    # identifica se é ESP32 ou site
    tipo = 'esp32' if client_ip == ESP32_IP else 'site'
    clientes.append({'ws': ws, 'tipo': tipo, 'ip': client_ip})
    print(f"[+] {client_ip} conectado como {tipo}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                text = msg.data.strip()
                cmd = None

                # tenta JSON
                try:
                    j = json.loads(text)
                    # se veio identidade, só marca e continua
                    if 'identidade' in j:
                        for c in clientes:
                            if c['ws'] is ws:
                                c['tipo'] = j['identidade']
                                print(f"    -> reclassificado como {j['identidade']}")
                        continue
                    # se veio { "comando": "ligar" }
                    if 'comando' in j:
                        cmd = j['comando']
                except json.JSONDecodeError:
                    # se não for JSON, trata text puro
                    cmd = text

                if cmd and tipo == 'site':
                    print(f"[cmd] do site → {cmd}")
                    # envia só para ESP32
                    for c in clientes:
                        if c['tipo'] == 'esp32' and not c['ws'].closed:
                            await c['ws'].send_str(cmd)

            elif msg.type == web.WSMsgType.ERROR:
                print(f"[!] WebSocket error ({client_ip}): {ws.exception()}")

    finally:
        # remove ao desconectar
        clientes[:] = [c for c in clientes if c['ws'] is not ws]
        print(f"[-] {client_ip} desconectou")

    return ws

app = web.Application()
app.add_routes(routes)
# serve tudo de public/ como /
app.router.add_static('/', path='public', name='static')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"▶️ Iniciando em 0.0.0.0:{port}, ESP32_IP={ESP32_IP}")
    web.run_app(app, port=port)
