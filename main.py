from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()
rooms = {} # База данных комнат в реальном времени: {room_id: {"players": {}, "preset": "mafia", "board": [""]*9}}

@app.websocket("/ws/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    await websocket.accept()
    if room_id not in rooms:
        rooms[room_id] = {"players": {}, "preset": "mafia", "board": [""] * 9, "turn": "X"}
    
    rooms[room_id]["players"][username] = websocket
    await sync_room(room_id)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            room = rooms[room_id]

            if msg["action"] == "preset":
                room["preset"] = msg["preset"]
                await sync_room(room_id)
                
            elif msg["action"] == "move":
                idx = msg["index"]
                if room["board"][idx] == "" and room["preset"] == "mafia":
                    room["board"][idx] = room["turn"]
                    room["turn"] = "O" if room["turn"] == "X" else "X"
                    await sync_room(room_id)
                    
    except WebSocketDisconnect:
        if room_id in rooms and username in rooms[room_id]["players"]:
            del rooms[room_id]["players"][username]
            if not rooms[room_id]["players"]:
                del rooms[room_id]
            else:
                await sync_room(room_id)

async def sync_room(room_id: str):
    if room_id in rooms:
        room = rooms[room_id]
        packet = {
            "type": "sync",
            "players": list(room["players"].keys()),
            "preset": room["preset"],
            "board": room["board"]
        }
        for ws in room["players"].values():
            try: await ws.send_text(json.dumps(packet))
            except: pass
