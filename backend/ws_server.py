from websockets.server import serve
import asyncio
from uuid import uuid4
import json
import os


clients = {}

async def handler(websocket):
    # Receive first message (user name)
    first_message = await websocket.recv()
    data = json.loads(first_message)
    
    if data["type"] == "join":
        name = data["name"]
        clients[websocket] = name
        print(f"{name} joined the chat.")

        # Notify all clients
        await broadcast(f"{name} joined the chat!", "Server")

    try:
        async for message in websocket:
            data = json.loads(message)
            await broadcast(data["message"], data["name"])
    except:
        pass
    finally:
        if websocket in clients:
            name = clients.pop(websocket)
            print(f"{name} left the chat.")
            await broadcast(f"{name} left the chat.", "Server")

async def broadcast(message, sender):
    data = json.dumps({"name": sender, "message": message})
    for client_conn, user in clients.items():
        if sender != user:
            await client_conn.send(data)
    

async def main():
    port = int(os.getenv("PORT", 8000))
    async with serve(handler, "0.0.0.0", port) as server:
        print("running on ws:localhost:9090....")
        await server.serve_forever()

if __name__ == "__main__":
  asyncio.run(main())



