import webview
import os
import sys

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

game_file = os.path.join(application_path, 'game.html')

print("Запуск клиента NEXUS...")
webview.create_window('NEXUS Game Client', game_file, width=1024, height=768)
webview.start(http_server=True)
