#!/usr/bin/env python

import asyncio
import datetime
import random
import websockets
import traceback
from game import CompetitiveWordle

game = CompetitiveWordle()

connected = set()

users = {}


async def consumer(message, socket):
    if "handshake" in message and ":" in message:
        username = message.split(":")[1]
        game.add_player(username)
        users[username] = socket


async def sync_game():
    await asyncio.sleep(1)
    for user, socket in users.items():
        if socket.open:
            await socket.send(user)
    return True


async def handler(websocket, path):
    while True:
        listener_task = asyncio.ensure_future(websocket.recv())
        producer_task = asyncio.ensure_future(sync_game())
        done, pending = await asyncio.wait(
            [listener_task, producer_task], return_when=asyncio.FIRST_COMPLETED
        )

        if listener_task in done:
            message = listener_task.result()
            await consumer(message, websocket)
        else:
            listener_task.cancel()

        if producer_task in done:
            message = producer_task.result()
        else:
            producer_task.cancel()

        await asyncio.sleep(0.01)


start_server = websockets.serve(handler, "127.0.0.1", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
