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

        # Add user to Redis active users list
        await r.sadd("active_users", name)

        # send the last 10 messages from the rdb
        messages = await r.lrange("chat_messages", -10, -1)
        for msg in messages:
            await websocket.send(msg)

        # Broadcast new user list
        await broadcast_active_users(r)

        # Notify all clients
        await broadcast(f"{name} joined the chat!", "Server", r)

    try:
        async for message in websocket:
            data = json.loads(message)
            receiver = data.get('receiver')
            if receiver:
                await broadcast_to_specific_user(data['message'], data['name'], receiver)
            else:
                chat_message = json.dumps({"name": data["name"], "message": data["message"]})

                # Store message in Redis
                await r.rpush("chat_messages", chat_message)
                await r.ltrim("chat_messages", -50, -1)  # Keep only last 50 messages

                await broadcast(data["message"], data["name"], r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if websocket in clients:
            name = clients.pop(websocket)
            print(f"{name} left the chat.")

            # Remove user from Redis
            await r.srem("active_users", name)

            await broadcast(f"{name} left the chat.", "Server", r)

            # Broadcast updated user list
            await broadcast_active_users(r)

async def broadcast(message, sender, r):
    data = json.dumps({"type": "message", "name": sender, "message": message})
    for client in clients:
            await client.send(data)

async def broadcast_active_users(r):
    """Send the updated active user list to all clients"""
    active_users = list(await r.smembers("active_users"))
    data = json.dumps({"type": "active_users", "users": active_users})
    for client in clients:
        try:
            await client.send(data)
        except Exception as e:
            print(f"Error sending user list: {e}")

async def broadcast_to_specific_user(message, sender, receiver):
    data = json.dumps({"type": "private_message", "name": sender, "message": message, "receiver": receiver})
    for conn, user in clients.items():
        receiver_conn = None
        sender_conn = None

        if user == receiver:
            receiver_conn = conn
        if user == sender:
            sender_conn = conn

        if receiver_conn:
            try:
                await receiver_conn.send(data)
            except Exception as e:
                print(f"Error sending private message: {e}")

        if sender_conn:
            try:
                await sender_conn.send(data)
            except Exception as e:
                print(f"Error sending private message: {e}")

        if not receiver_conn:
            print(f"Receiver {receiver} not found.")

async def main():
    port = int(os.getenv("PORT", 8000))
    async with serve(handler, "0.0.0.0", port) as server:
        print("running on ws:localhost:9090....")
        await server.serve_forever()

if __name__ == "__main__":
  asyncio.run(main())



