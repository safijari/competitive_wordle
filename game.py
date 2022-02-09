class GameState:
    def __init__(self, word, username):
        self.username = username
        self.word = word
        self.state = "ongoing"
        self.tries = []

    def make_guess(self, word):
        if len(self.tries) >= 6:
            print(f"ERROR: {self.username} tried playing more than 6 words")
            return None

        if self.check_if_won():
            print(f"ERROR: {self.username} has already won, can't play word")
            return "C" * len(word)

        self.tries.append(word)
        print(self.tries)

        out = []
        for c1, c2 in zip(word, self.word):
            if c1 == c2:
                out.append("C")
                continue
            if c1 in self.word:
                out.append("P")
                continue
            if c1 not in self.word:
                out.append("X")

        self.check_if_won()

        return "".join(out)

    def check_if_won(self):
        return len(self.tries) and self.tries[-1] == self.word

    @property
    def score(self):
        return 6 - len(self.tries)


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


class CompetitiveWordle:
    def __init__(self):
        self.players = {}
        self.word = ""

    def add_player(self, username):
        if username not in self.players:
            self.players[username] = WordlePlayerState(username)

    def select_word(self, word):
        self.word = word
        print(f"Starting new game: {word}")
        for player_name, state in self.players.items():
            state.new_game(word)

    def play(self, indict):
        res = {}
        for player_name, guess in indict.items():
            print(f"{player_name} played {guess}")
            res[player_name] = self.players[player_name].make_guess(guess)

            print(f"{player_name} has score {self.players[player_name].score}")

        print(res)


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
