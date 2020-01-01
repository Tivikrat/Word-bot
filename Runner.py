import functools
from random import randrange
from time import time

from Statistics import statistics
import honchar
from honchar import start, next_move, dictionary_path


def get_answer(word, attempt):
    matched, exact = 0, 0
    for i, letter in enumerate(attempt):
        if letter in word:
            matched += 1
        if letter == word[i]:
            exact += 1
    return matched, exact


def timing(function=None, *, limit=None, message=None):
    if function is None:
        return lambda func: timing(func, limit=limit, message=message)

    @functools.wraps(function)
    def inner(*args, **kwargs):
        start_time = time()
        result = function(*args, **kwargs)
        elapsed_time = time() - start_time
        if limit is not None and elapsed_time > limit:
            print("Time Limit Exceeded")
        if message is not None:
            print(message, end="")
        print(elapsed_time)
        return result

    return inner


class BullCowsError(Exception):
    pass


class WrongWordLengthError(BullCowsError):
    pass


class AbsentWordError(BullCowsError):
    pass


class NotWordError(BullCowsError):
    pass


class Runner:
    @staticmethod
    def generate_words(length, number):
        with open(dictionary_path, "r", encoding='UTF-8') as file:
            dictionary = \
                [word
                 for word in map(str.strip, file.readlines())
                 if len(word) == length
                 and len(word) == len(set(word))]
            for _ in range(number):
                yield dictionary[randrange(len(dictionary))]

    @timing(limit=0, message="Single game was ran with seconds: ")
    def run_game(self, word: str):
        print(f'[sys]: Загадано слово "{word}"')
        length = len(word)
        with open(dictionary_path, "r", encoding='UTF-8') as file:
            dictionary = \
                [word
                 for word in map(str.strip, file.readlines())
                 if len(word) == length
                 and len(word) == len(set(word))]

        attempt = start(length)
        print(f'[run]: >> Вызвана функция `start({length})`, '
              f'где {length} - длина загаданного слова')

        print(f'[bot]: << Бот ответил первой попыткой: "{attempt}"\n')
        attempts_count = 1
        while attempt != word:
            if not isinstance(attempt, str):
                raise NotWordError
            if len(attempt) != length:
                raise WrongWordLengthError
            if attempt not in dictionary:
                raise AbsentWordError

            print(f'[sys]: Бот ещё не отгадал слово, считаем для него ответ.')
            match, exact = get_answer(word, attempt)
            print(f'[sys]: Получили `match = {match}` и `exact = {exact}`\n')

            attempt = next_move(match, exact)
            print(f'[run]: >> Вызвана функция `next_move({match}, {exact})`')
            print(f'[bot]: << Бот ответил следующей попыткой: "{attempt}"\n')
            attempts_count += 1
            print(
                f'[sys]: Нарастили счётчик попыток,'
                f' теперь их {attempts_count}')
        return attempts_count

    def _run_games(self, *words):
        for word in words:
            if isinstance(word, str):
                self.run_game(word)
            else:
                self._run_games(*word)

    @timing(limit=0, message="Games were ran with seconds: ")
    def run_games(self, *words):
        self._run_games(*words)

    @timing(limit=10, message="Parametrized games were ran with seconds: ")
    def run_parametrized_games(self, length: int, number: int):
        self._run_games(Runner.generate_words(length, number))


with statistics("stats.txt") as stats:
    honchar.stats = stats
    runner = Runner()
    runner.run_parametrized_games(5, 1)
    print(stats[4])
    print(stats)
    with statistics("stats1.txt") as other_stats:
        print(stats > other_stats)
        print(stats < other_stats)
        print(stats == other_stats)
    print("standard search")
    print(stats.search_words("вы"))
    print(stats.search_words("і"))
    print("x-vowels")
    print(stats.search_words("1-vowel"))
    print(stats.search_words("2-vowel"))
    print(stats.search_words("3-vowel"))
    print(stats.search_words("10-vowel"))
    print("x-consonants")
    print(stats.search_words("1-consonant"))
    print(stats.search_words("2-consonant"))
    print(stats.search_words("3-consonant"))
    print(stats.search_words("10-consonant"))
    print("x-consecutive-vowels")
    print(stats.search_words("1-consecutive-vowels"))
    print(stats.search_words("2-consecutive-vowels"))
    print(stats.search_words("3-consecutive-vowels"))
    print(stats.search_words("10-consecutive-vowels"))
    print("x-consecutive-consonants")
    print(stats.search_words("1-consecutive-consonants"))
    print(stats.search_words("2-consecutive-consonants"))
    print(stats.search_words("3-consecutive-consonants"))
    print(stats.search_words("10-consecutive-consonants"))
