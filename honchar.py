from collections import namedtuple

from Statistics import Statistics

dictionary_path = "Словарь.txt"
dictionary_list = []
word_size = 0
attempt = ''
stats = Statistics("Honchar")
paper = None


class Paper:
    def __init__(self):
        self.word_result = namedtuple('word_result',
                                      ['word', 'match', 'exact'])
        self.results = []

    def push(self, word: str, match: int, exact: int):
        print(f"Записую на папірець до слова \"{word}\""
              f" match = {match} і exact = {exact}")
        self.results += [self.word_result(word=word, match=match, exact=exact)]


def get_answer(word, attempt):
    matched, exact = 0, 0
    for i, letter in enumerate(attempt):
        if letter in word:
            matched += 1
        if letter == word[i]:
            exact += 1
    return matched, exact


def get_word():
    global attempt
    global paper
    for word in dictionary_list:
        for result in paper.results:
            match, exact = get_answer(word, result.word)
            if result.match != match or result.exact != exact:
                break
        else:
            attempt = word
            stats.save_move_word(attempt)
            if len(paper.results) > 0:
                print(f"Вгадано слово \"{attempt}\", бо воно має:")
                for index, result in enumerate(paper.results):
                    print(f"{index + 1}) зі словом \"{result.word}\""
                          f" {result.match} спільних букв,"
                          f" з яких {result.exact} на однакових місцях")
            else:
                print(f"Вгадано перше слово \"{attempt}\"")
            return attempt


def start(length: int):
    stats.new_game()
    global word_size
    global dictionary_list
    global paper
    paper = Paper()
    word_size = length
    with open(dictionary_path, "r", encoding='UTF-8') as file:
        dictionary_list = \
            [word
             for word in map(str.strip, file.readlines())
             if len(word) == length
             and len(word) == len(set(word))]
    return get_word()


def next_move(match: int, exact: int) -> str:
    global attempt
    global dictionary_list
    paper.push(attempt, match, exact)
    dictionary_list = \
        [word
         for word in dictionary_list
         if (get_answer(word, attempt) == (match, exact))]
    return get_word()
