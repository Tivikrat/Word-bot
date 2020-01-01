import re
from collections import Counter, defaultdict, namedtuple
from os.path import exists


class statistics:
    def __init__(self, filename: str):
        self.filename = filename

    def __enter__(self):
        if exists(self.filename):
            with open(self.filename, 'r', encoding='UTF-8') as file:
                games = []
                name = file.readline()[6:].strip()
                file.readline()
                line = file.readline()
                while line[0] != 's':
                    game_attempts = []
                    line = file.readline()
                    while 'o' != line[2] != '-':
                        game_attempts += [line[6:].strip()]
                        line = file.readline()
                    games += [game_attempts]
                self.stats = Statistics(name, games)
        else:
            self.stats = Statistics()
        return self.stats

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stats.export(self.filename)


class Statistics:
    class Iterator:
        game_index = 0
        attempt_index = 0

        def __init__(self, instance):
            self.instance = instance

        def __next__(self):
            if len(self.instance.games) <= self.game_index:
                raise StopIteration
            game = self.instance.games[self.game_index]
            if len(game) <= self.attempt_index:
                self.game_index += 1
                self.attempt_index = 0
                return self.__next__()
            self.attempt_index += 1
            return game[self.attempt_index - 1]

    name = "Unnamed"
    score = namedtuple('score',
                       ['won', 'unknown', 'attempts_total',
                        'attempts_average'])
    games = []
    _max_attempts = float('inf')

    @property
    def games_count(self):
        return len(self.games)

    @property
    def won(self):
        return self.games_count - self.unknown

    @property
    def unknown(self):
        max_attempts_count = max(len(attempts) for attempts in self.games)
        return len([len(attempts)
                    for attempts in self.games
                    if len(attempts) == max_attempts_count])

    @property
    def max_attempts(self):
        return self._max_attempts

    @max_attempts.setter
    def max_attempts(self, value):
        self._max_attempts = value
        for attempts in self.games:
            while len(attempts) > self._max_attempts:
                attempts.pop()

    def __getitem__(self, index):
        return self.games[index]

    def __str__(self):
        return f'Statistics for "{self.name}": ' \
               f'{self.won} wins and {self.unknown} unknown results'

    def __lt__(self, other):
        if self.won != other.won:
            return self.won < other.won
        if self.unknown != other.unknown:
            return other.unknown < self.unknown
        return other.name < self.name

    def __gt__(self, other):
        return other < self

    def __eq__(self, other):
        return not (self < other or other < self)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return other < self or self == other

    def __init__(self, name="Unnamed", games=None):
        self.name = name
        if games is not None:
            self.games = games

    def __iter__(self):
        return self.Iterator(self)

    def new_game(self):
        self.games += [[]]

    def save_move_word(self, attempt: str):
        self.games[-1] += [attempt]

    def save_move_result(self, match: int, exact: int):
        ...

    def get_data(self) -> dict:
        letters = Counter()
        words = defaultdict(list)
        for index, game in enumerate(self.games):
            for attempt in game:
                words[attempt] += [index]
                for letter in attempt:
                    letters[letter] += 1

        attempts_total = sum(
            [len(attempts) for attempts in self.games])
        attempts_average = attempts_total / self.games_count
        score = self.score(won=self.won, unknown=self.unknown,
                           attempts_total=attempts_total,
                           attempts_average=attempts_average)
        return {'games': self.games, 'letters': letters, 'words': words,
                'score': score}

    def export(self, filename: str):
        with open(filename, "w", encoding='UTF-8') as file:
            file.write(f"name: {self.name}\n")
            file.write("games:\n")
            for game_index, attempts in enumerate(self.games):
                file.write(f"  - {game_index}:\n")
                file.writelines(f"    - {attempt}\n" for attempt in attempts)
            file.write("score:\n")
            file.write(f"  won: {self.won}\n")
            file.write(f"  unknown: {self.unknown}\n")

    def search_words(self, pattern: str):
        attempts = list(set(attempt
                            for attempts in self.games
                            for attempt in attempts))
        vowels = 'ауоыиэяюёе'
        # all consonants is needed because of non-alpha symbols (-, ., ')
        consonants = 'бвгджзйклмнпрстфхцчшщ'

        def check_symbols_count(word, count, symbols):
            symbols_count = 0
            for letter in word:
                if letter.lower() in symbols:
                    symbols_count += 1
            return symbols_count == count

        def check_consecutive(word, count, symbols):
            # delete comma in regex for precise count
            # (equal or more when comma used)
            regex = r'[' + symbols + ']{' + str(count) + ',}'
            return re.search(regex, word) is not None

        def check_for_pattern(check_pattern: str, function, symbols):
            search = re.search(check_pattern, pattern)
            if search is not None:
                count = int(search.group(1))
                return [attempt
                        for attempt in attempts
                        if function(attempt, count, symbols)]
            return None

        checks = [[r'^(\d+)-vowel$', check_symbols_count, vowels],
                  [r'^(\d+)-consonant$', check_symbols_count, consonants],
                  [r'^(\d+)-consecutive-vowels$', check_consecutive, vowels],
                  [r'^(\d+)-consecutive-consonants$',
                   check_consecutive, consonants]]
        for check in checks:
            results = check_for_pattern(*check)
            if results is not None:
                return results

        return [attempt
                for attempt in attempts
                if re.search(pattern, attempt) is not None]
