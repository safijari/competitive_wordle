def score_guess(guess, word):
    out = []
    for c1, c2 in zip(guess, word):
        if c1 == c2:
            out.append("C")
            continue
        if c1 in word:
            out.append("P")
            continue
        if c1 not in word:
            out.append("X")

    return "".join(out)


class GameState:
    def __init__(self, word, username):
        self.username = username
        self.word = word
        self.state = "ongoing"
        self.tries = []

    def make_guess(self, word):
        if len(word) != 5:
            print(f"ERROR: {self.username} tried a word of incompatible length")
            return None

        if word in self.tries:
            print(f"ERROR: {self.username} tried playing the same word multiple times")
            return None

        if len(self.tries) >= 6:
            print(f"ERROR: {self.username} tried playing more than 6 words")
            return None

        if self.check_if_won():
            print(f"ERROR: {self.username} has already won, can't play word")
            return "C" * len(word)

        self.tries.append(word)

        out = score_guess(word, self.word)

        self.check_if_won()

        return out

    def check_if_won(self):
        return len(self.tries) and self.tries[-1] == self.word

    def check_if_over(self):
        return self.check_if_won() or len(self.tries) >= 6

    @property
    def score(self):
        return 7 - len(self.tries) if self.check_if_won() else 0


class WordlePlayerState:
    def __init__(self, username):
        self.username = username
        self.games = []

    def new_game(self, word):
        self.games.append(GameState(word, self.username))

    def make_guess(self, guess):
        assert self.games, "No games exists, can't make guess"
        game = self.games[-1]
        return game.make_guess(guess)

    @property
    def score(self):
        return sum([game.score for game in self.games if game.check_if_won()])

    def as_dict(self):
        game = self.games[-1]
        return {
            "username": self.username,
            "num_games": len(self.games) - 1,
            "score": self.score,
            "current_game_state": [
                [tr, score_guess(tr, game.word)] for tr in game.tries
            ],
        }

    def summary(self):
        game = self.games[-1]
        return {
            "username": self.username,
            "num_games": len(self.games) - 1,
            "score": self.score,
            "current_game_state": [
                ["", score_guess(tr, game.word)] for tr in game.tries
            ],
        }


class CompetitiveWordle:
    def __init__(self):
        self.players = {}
        self.word = ""

    def add_player(self, username):
        if username not in self.players:
            self.players[username] = WordlePlayerState(username)
            self.players[username].new_game(self.word)

    def select_word(self, word):
        self.word = word
        print(f"Starting new game")
        for player_name, state in self.players.items():
            state.new_game(word)

    def play(self, indict):
        res = {}
        for player_name, guess in indict.items():
            res[player_name] = self.players[player_name].make_guess(guess)

            print(f"{player_name} played a guess and got response {res[player_name]}")
            print(f"{player_name} has score {self.players[player_name].score}")


def main():
    game = CompetitiveWordle()
    game.add_player("jari")
    game.add_player("cem")
    game.select_word("perky")

    game.play({"jari": "porky", "cem": "wordle"})
    game.play({"jari": "perky", "cem": "first"})
    game.play({"jari": "jerky", "cem": "perky"})
    game.play({"jari": "jerky", "cem": "crepe"})

    game.select_word("frost")

    game.play({"jari": "porky", "cem": "wordle"})
    game.play({"jari": "perky", "cem": "first"})
    game.play({"jari": "jerky", "cem": "frost"})
    game.play({"jari": "jerky", "cem": "crepe"})


if __name__ == "__main__":
    main()
