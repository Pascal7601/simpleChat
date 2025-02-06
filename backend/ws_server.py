from websockets.server import serve
import asyncio
from uuid import uuid4
import json
import os
import redis.asyncio as redis



REDIS_URL = "redis://red-cuiai9lds78s73dvbmag:6379"
clients = {}

async def get_redis():
    return await redis.from_url(REDIS_URL, decode_responses=True)

async def handler(websocket):
    r = await get_redis()
    # Receive first message (user name)
    first_message = await websocket.recv()
    data = json.loads(first_message)
    
    if data["type"] == "join":
        name = data["name"]
        clients[websocket] = name
        print(f"{name} joined the chat.")

        # send the last 10 messages from the rdb
        messages = await r.lrange("chat_messages", -10, -1)
        for msg in messages:
            await websocket.send(msg)

        # Notify all clients
        await broadcast(f"{name} joined the chat!", "Server", r)

    try:
        async for message in websocket:
            data = json.loads(message)
            chat_message = json.dumps({"name": data["name"], "message": data["message"]})

            # Store message in Redis
            await r.rpush("chat_messages", chat_message)
            await r.ltrim("chat_messages", -50, -1)  # Keep only last 50 messages

            await broadcast(data["message"], data["name"], r)
    except:
        pass
    finally:
        if websocket in clients:
            name = clients.pop(websocket)
            print(f"{name} left the chat.")
            await broadcast(f"{name} left the chat.", "Server", r)

async def broadcast(message, sender, r):
    data = json.dumps({"name": sender, "message": message})
    for client in clients:
            await client.send(data)
    

async def main():
    port = int(os.getenv("PORT", 8000))
    async with serve(handler, "0.0.0.0", port) as server:
        print("running on ws:localhost:9090....")
        await server.serve_forever()

if __name__ == "__main__":
  asyncio.run(main())



