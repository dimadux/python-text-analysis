import json
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re


class ParsingModule:
    @staticmethod
    def dump_json_object(file_name, json_object):
        serialized_object = json.dumps(json_object)
        file = open(file_name, "w")
        file.write(serialized_object)
        file.close()

    def raise_syntax_error(self, sentence):
        is_ignore_errors = self.get_config_value("IGNORE_PARSING_ERRORS") == "1"
        message = "Wrong brackets syntax at sentence: {0}".format(sentence)

        if is_ignore_errors:
            print(message)
        else:
            raise SyntaxError(message)

    def get_brackets_indices(self, sentence, start_index):
        i = start_index
        start_index = -1
        end_index = -1
        counter = 0

        while i < len(sentence):
            if sentence[i] == "<":
                counter += 1
                if start_index == -1:
                    start_index = i

            if sentence[i] == ">":
                counter -= 1
                if start_index != -1:
                    end_index = i

            if counter < 0:
                self.raise_syntax_error(sentence)
                return -1, -1

            if end_index != -1 and counter == 0:
                return start_index, end_index

            i += 1

        if counter != 0:
            self.raise_syntax_error(sentence)
            return -1, -1
        elif start_index >= 0:
            return start_index, end_index
        else:
            return -1, -1

    def parse_config_value(self, line):
        line = line.replace("\t", " ")
        line = " ".join(line.split())
        cfg = line.split(" ", 1)
        if len(cfg) != 2:
            raise SyntaxError("Wrong config syntax at line:\n\t{0}".format(line))
        self.config[cfg[0]] = cfg[1]

    def read_config_file(self):
        file_name = "config.config"
        file = open(file_name, "r")
        [self.parse_config_value(l) for l in file.readlines()]

    def get_config_value(self, key):
        if key not in self.config:
            raise KeyError("Missing key {0} in config file".format(key))
        return self.config[key]

    def read_test_text(self):
        file_name = self.get_config_value("TEST_TEXT_FILE_NAME")
        file = open(file_name, "r")
        language = self.get_config_value("LANGUAGE")
        self.test_sentences = sent_tokenize(file.read(), language)

    def get_stop_words(self):
        language = self.get_config_value("LANGUAGE")
        result = set(stopwords.words(language))

        result.add("<")
        result.add(">")
        result.add(",")
        result.add(".")
        result.add("!")
        result.add("?")

        i = ord("A")
        while i <= ord("Z"):
            result.add(chr(i))
            i += 1

        return result

    def extract_definition(self, sentence, stemmer):
        start_index, end_index = self.get_brackets_indices(sentence, 0)

        if start_index < 0 or end_index < 0:
            return

        info = sentence[start_index + 1:end_index]
        end_info_index = len(info) - 1
        emotions = []
        while end_info_index > 0 and (info[end_info_index] <= "a" or "z" <= info[end_info_index]):
            if "A" <= info[end_info_index] <= "Z":
                emotions.append(info[end_info_index])
            end_info_index -= 1

        language = self.get_config_value("LANGUAGE")
        words = word_tokenize(info[:end_info_index + 1], language)

        stop_words = self.get_stop_words()
        words = [stemmer.stem(self.word_regex.sub("", w)) for w in words if w not in stop_words]

        self.definitions.append((words, emotions, info))

        self.extract_definition(info, stemmer)
        self.extract_definition(sentence[end_index + 1:], stemmer)

    def collect_definitions(self):
        stemmer = PorterStemmer()
        for sentence in self.test_sentences:
            self.extract_definition(sentence, stemmer)

    def collect_unique_words(self):
        for definition in self.definitions:
            for word in definition[0]:
                if word != "":
                    if word not in self.unique_words:
                        self.unique_words[word] = 1
                    else:
                        self.unique_words[word] += 1

    def dump_definitions(self):
        file_name = self.get_config_value("DEFINITIONS_FILE_NAME")
        ParsingModule.dump_json_object(file_name, self.definitions)

    def dump_unique_words(self):
        file_name = self.get_config_value("UNIQUE_WORDS_FILE_NAME")
        ParsingModule.dump_json_object(file_name, self.unique_words)

    def dump_sorted_unique_words(self, sort_by_alphabet, reverse):
        words = []
        for word in self.unique_words:
            words.append({"word": word, "count": self.unique_words[word]})
        file_name = self.get_config_value("SORTED_UNIQUE_WORDS_FILE_NAME")

        sort_key = "word" if sort_by_alphabet else "count"
        words = sorted(words, key=lambda k: k[sort_key], reverse=reverse)

        ParsingModule.dump_json_object(file_name, words)

    def __init__(self):
        self.config = {}
        self.read_config_file()
        self.test_sentences = []
        self.definitions = []
        self.unique_words = {}
        self.word_regex = re.compile("[^a-zA-Z]")


if __name__ == "__main__":
    parsing = ParsingModule()
    parsing.read_test_text()

    parsing.collect_definitions()
    parsing.collect_unique_words()

    parsing.dump_definitions()
    parsing.dump_unique_words()
    parsing.dump_sorted_unique_words(False, True)

    # print(parsing.test_sentences)
    # print()
    # print(parsing.definitions)
    # print(parsing.unique_words)

    # for sentence in parsing.test_sentences:
    #     start_index, end_index = parsing.get_brackets_indices(sentence, 0)
    #
    #     print(sentence[start_index + 1:end_index])

    # parsing.get_words_definitions()
    #
    # print(parsing.config)
    # print(parsing.test_sentences)
