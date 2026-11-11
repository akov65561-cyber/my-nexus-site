import webview
import threading
import asyncio
import websockets
import json
import os
import sys

# ПУТЬ ДЛЯ СОХРАНЕНИЯ ДАННЫХ (как ты просил)
DATA_DIR = r"C:\Users\user\Desktop\ДАТА\ИГРОКИ"

# Создаем папку, если ее нет
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

connected_clients = {}

async def server_handler(websocket):
    client_id = str(id(websocket))
    print(f"Игрок {client_id} подключился!")
    
    player_data = {"id": client_id, "x": 0.0, "y": 0.0, "facing": "down", "moving": False}
    
    init_players = {cid: client["data"] for cid, client in connected_clients.items()}
    await websocket.send(json.dumps({"type": "init", "players": init_players}))
    
    connected_clients[client_id] = {"ws": websocket, "data": player_data}
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if "type" in data and data["type"].startswith("voice-"):
                target = data.get("target")
                if target in connected_clients:
                    data["id"] = client_id
                    await connected_clients[target]["ws"].send(json.dumps(data))
                continue

            connected_clients[client_id]["data"].update(data)
            payload = json.dumps({"type": "update", "id": client_id, "data": data})
            
            tasks = [client["ws"].send(payload) for cid, client in connected_clients.items() if cid != client_id]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if client_id in connected_clients:
            # СОХРАНЯЕМ ДАННЫЕ ИГРОКА НА ПК ПРИ ВЫХОДЕ
            try:
                save_path = os.path.join(DATA_DIR, f"player_{client_id}.json")
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(connected_clients[client_id]["data"], f, ensure_ascii=False, indent=4)
                print(f"Данные сохранены в {save_path}")
            except Exception as e:
                print(f"Ошибка сохранения: {e}")

            del connected_clients[client_id]
            payload = json.dumps({"type": "disconnect", "id": client_id})
            tasks = [client["ws"].send(payload) for client in connected_clients.values()]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

def start_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def run():
        async with websockets.serve(server_handler, "localhost", 8765):
            await asyncio.Future()
            
    print("Сервер запущен внутри клиента!")
    loop.run_until_complete(run())

# Запускаем сервер в фоновом потоке (игрок об этом не знает)
threading.Thread(target=start_server, daemon=True).start()

# Открываем окно клиента (как в Роблоксе)
if getattr(sys, 'frozen', False):
    # Если запущено как .exe
    application_path = sys._MEIPASS
else:
    # Если запущено как .py
    application_path = os.path.dirname(os.path.abspath(__file__))

html_file = os.path.join(application_path, 'index.html')

print("Запуск игрового окна...")
webview.create_window('NEXUS Client', html_file, width=1024, height=768)
webview.start()