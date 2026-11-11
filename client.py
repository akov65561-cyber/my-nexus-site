import webview
import threading
import asyncio
import websockets
import json
import os
import sys

# ПУТЬ ДЛЯ СОХРАНЕНИЯ ДАННЫХ
DATA_DIR = r"C:\Users\user\Desktop\ДАТА\ИГРОКИ"

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

# Запускаем сервер в фоне
threading.Thread(target=start_server, daemon=True).start()

# --- НАДЕЖНЫЙ ПОИСК ФАЙЛА ---
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# ВНИМАНИЕ: ТЕПЕРЬ МЫ ЗАГРУЖАЕМ ИГРУ, А НЕ САЙТ!
game_file = os.path.join(application_path, 'game.html')

if not os.path.exists(game_file):
    print(f"ОШИБКА: Файл game.html не найден по пути: {game_file}")
    print("Убедитесь, что файлы client.py и game.html лежат в ОДНОЙ папке!")
    input("Нажмите Enter, чтобы закрыть...")
    sys.exit()

print(f"Запуск игрового окна: {game_file}")
webview.create_window('NEXUS Game Client', game_file, width=1024, height=768)
webview.start()
