from sanic import Sanic
import sanic
from sanic.response import redirect
from game import CompetitiveWordle
import asyncio
import json
import traceback
from random import choice

from dictionary import to_choose, allowed_words

all_words = to_choose + allowed_words

to_choose = [w for w in to_choose if len(set(w)) == 5]
print(len(to_choose), "total words")


to_choose = set(to_choose)
chosen = set()

game = CompetitiveWordle()

connected = set()

def start_new_game():
    word = choice(list(to_choose.difference(chosen)))
    chosen.add(word)
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


async def sync_game():
    print("syncing")
    await asyncio.sleep(1.0)
    summaries = [game.players[user].summary() for user in users]
    for user, socket in users.items():
        try:
            await socket.send(
                json.dumps(
                    {
                        "type": "state",
                        "data": game.players[user].as_dict(),
                        "summaries": summaries,
                    }
                )
            )
        except Exception:
            print(f"Can't sync to {user}, will try next time")

    if all([game.players[user].games[-1].check_if_over() for user in users]):
        print("starting new game")
        start_new_game()
    return True


@app.websocket("/game")
async def feed(request, websocket):
    print(request, websocket)
    while True:
        await consumer(websocket)
        await sync_game()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
