from sanic import Sanic
import sanic
from sanic.response import redirect
from game import CompetitiveWordle
import asyncio
import json
import traceback
from random import choice
import time

from dictionary import to_choose, allowed_words

all_words = to_choose + allowed_words

to_choose = [w for w in to_choose if len(set(w)) == 5]


to_choose = set(to_choose)
chosen = list()

game = CompetitiveWordle()

connected = set()

def start_new_game():
    word = choice(list(to_choose.difference(set(chosen))))
    chosen.append(word)
    game.select_word(word)

start_new_game()

users = {}


app = Sanic("Example")


app.static("index.html", "index.html")


@app.route("/")
def index(request):
    return redirect("index.html")


async def consumer(socket):
    message = await socket.recv(0.1)
    if message and "handshake" in message and ":" in message:
        username = message.split(":")[1]
        game.add_player(username)
        users[username] = socket
        await socket.send(json.dumps({"type": "dictionary", "data": all_words}))
        return True

    if message and "guess" in message and len(message.split(":")) == 3:
        _, username, guess = message.split(":")
        game.play({username: guess})
        return True

    if message and "kick_player" in message and len(message.split(":")) == 2:
        player = message.split(":")[1]
        try:
            del users[player]
            try:
                del game.players[player]
            except Exception:
                print(f"Could not fully kick player {player}")
        except Exception:
            print(f"Could not fully kick player {player}")

    return False


async def sync_game(in_socket):
    print("syncing")
    # await asyncio.sleep(1.0)
    summaries = [game.players[user].summary() for user in users]
    for user, socket in users.items():
        if socket != in_socket:
            continue
        try:
            await socket.send(
                json.dumps(
                    {
                        "type": "state",
                        "data": game.players[user].as_dict(),
                        "summaries": summaries,
                        "previous_words": chosen[:-1]
                    }
                )
            )
        except Exception:
            print(f"Can't sync to {user}, will try next time")

    if game.players and all([game.players[user].games[-1].check_if_over() for user in users]):
        print("starting new game")
        start_new_game()
    return True


@app.websocket("/game")
async def feed(request, websocket):
    last_sync = time.time()
    while True:
        do_sync = await consumer(websocket)
        if time.time() - last_sync > 1.0 or do_sync:
            last_sync = time.time()
            await sync_game(websocket)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
