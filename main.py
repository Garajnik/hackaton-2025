from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time
from threading import Thread
from datetime import datetime


app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов
socketio = SocketIO(app, cors_allowed_origins="*")  # Разрешаем подключение WebSocket с любого домена

# Функция для отправки логов клиенту
def send_log(sid, message):
    log_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Текущее время
        "message": message
    }
    socketio.emit('log', log_data, room=sid)  # Отправляем лог клиенту

# Функция, которая будет отправлять JSON через 5 секунд после подключения
def send_json_after_delay(sid):
    time.sleep(5)  # Ждем 5 секунд
    data = '{"startTime": "11:11","endTime": "20:47", "stall": "120", "stage": "Промывка", "comment": "Без замечаний"}'
    socketio.emit('json_data', data, room=sid)  # Отправляем JSON клиенту
    send_log(sid, "JSON data sent to client.")  # Логируем отправку JSON

# Обработчик события подключения WebSocket
@socketio.on('connect')
def handle_connect():
    sid = request.sid  # Получаем идентификатор сессии клиента
    send_log(sid, "Client connected.")  # Логируем подключение клиента
    thread = Thread(target=send_json_after_delay, args=(sid,))
    thread.start()  # Запускаем поток, который отправит JSON через 5 секунд

# Обработчик события отключения WebSocket
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid  # Получаем идентификатор сессии клиента
    send_log(sid, "Client disconnected.")  # Логируем отключение клиента

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)