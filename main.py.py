from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Разрешаем подключение с любых устройств и доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище активных комнат и подключений игроков
# Структура: { room_id: { username: websocket } }
rooms = {}

# Заготовки игровых раундов
GAME_DATA = {
    "corrupted": "«Разделяй доходы правильно — забирай всё себе!»",
    "options": [
        "Мафия полностью перекрасила фон плаката",
        "Мафия подменила буквы в словах, превратив экологию в эгоизм 🌟",
        "Текст изменился из-за сбоя принтера"
    ]
}

@app.get("/")
def read_root():
    return {"status": "Сетевой сервер Сломанного Плаката активен!"}

@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    await websocket.accept()
    
    # Инициализируем комнату, если её ещё нет
    if room_id not in rooms:
        rooms[room_id] = {}
        
    # Добавляем игрока в комнату
    rooms[room_id][username] = websocket
    
    # Рассылаем всем в комнате обновленный список игроков
    await broadcast_players(room_id)
    
    try:
        while True:
            # Ждем команды от клиента (например, запуск игры лидером лобби)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "start":
                # Отправляем всем устройствам в комнате команду на старт игры и первый раунд
                start_packet = {
                    "type": "start_game",
                    "corrupted": GAME_DATA["corrupted"],
                    "options": GAME_DATA["options"]
                }
                await broadcast_to_room(room_id, start_packet)
                
    except WebSocketDisconnect:
        # Убираем игрока из подключений при отключении интернета
        if room_id in rooms and username in rooms[room_id]:
            del rooms[room_id][username]
            if not rooms[room_id]:
                del rooms[room_id]
            else:
                await broadcast_players(room_id)

async def broadcast_players(room_id: str):
    """Отправка списка всех подключенных игроков текущей комнаты"""
    if room_id in rooms:
        packet = {
            "type": "players_update",
            "players": list(rooms[room_id].keys())
        }
        await broadcast_to_room(room_id, packet)

async def broadcast_to_room(room_id: str, packet: dict):
    """Отправка сообщения абсолютно всем устройствам внутри одной комнаты"""
    if room_id in rooms:
        payload = json.dumps(packet)
        for ws in rooms[room_id].values():
            try:
                await ws.send_text(payload)
            except:
                pass
