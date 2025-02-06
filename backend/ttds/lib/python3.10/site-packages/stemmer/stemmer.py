import os
class Stemmer:
    # Stores the words loaded from the words.txt file
    words = set()
    # Stores the suffixes loaded from the suffix.txt file
    suffixes = []
    # Stores all possible stems of a word
    stems = []

    script_dir = os.path.dirname(__file__)

    # Constructor of the Stemmer class
    def __init__(self):
        # Loads words from the words.txt file
        self.__load_words()
        # Loads suffixes from the suffix.txt file
        self.__load_suffixes()

    # Destructor of the Stemmer class
    def __del__(self):
        # Clear both lists to free the memory space
        self.words.clear()
        self.suffixes.clear()

    # Loads the words from the word.txt file into memory
    def __load_words(self):
        file_path = os.path.join(self.script_dir, 'words.txt')
        # Open words.txt file in read mode with utf-8 encoding.
        with open(file_path, "r", encoding="utf8") as words_file:
            # Iterate over each line in the words.txt file
            for word in words_file:
                # Trim the spaces and newline characters from the string before adding to the list
                self.words.add(word.strip())

    # Loads the suffixes from the suffix.txt file into memory
    def __load_suffixes(self):
        file_path = os.path.join(self.script_dir, 'suffix.txt')
        # Open suffix.txt file in read mode with utf-8 encoding
        with open(file_path, "r", encoding="utf8") as suffix_file:
            # Iterate over each line in the suffix.txt file
            for suffix in suffix_file:
                # Trim the spaces and newline characters from the string before adding to the list
                self.suffixes.append(suffix.strip())

    # Removes one suffix at a time
    def suffix(self, word):
        word = word
        for suffix in self.suffixes:
            if word.endswith(suffix) and (word[:word.rfind(suffix)] in self.words):
                word = word[:word.rfind(suffix)]
                return word
            elif word.endswith(suffix):
                word = word[:word.rfind(suffix)]
                return word
        return word

    # Converts changed suffixes and roots to their original forms
    def converter(self, word):
        if word.endswith('lığ') or word.endswith('luğ') or word.endswith('lağ') or word.endswith('cığ'):
            l=list(word); l[-1]='q'; return "".join(l)
        elif word.endswith('liy') or word.endswith('lüy'):
            l=list(word); l[-1]='k'; return "".join(l)
        elif word.endswith('cağ'):
            l=list(word); l[-1]='q'; return "".join(l)
        elif word.endswith('cəy'):
            l=list(word); l[-1]='k'; return "".join(l)
        elif word.endswith('ığ') or word.endswith('uğ') or word.endswith('ağ'):
            l=list(word); l[-1]='q'; return "".join(l)
        elif word.endswith('iy') or word.endswith('üy') or word.endswith('əy'):
            l=list(word); l[-1]='k'; return "".join(l)
        elif word == 'ed':
            l=list(word); l[1]='t'; return "".join(l)
        elif word == 'ged':
            l=list(word); l[2]='t'; return "".join(l)
        return word

    # Returns the stemmed version of word
    def stem_word(self, word):
        # Change the word to lowercase.
        word = word.lower()

        for i in range(10):
            if word in self.words:
                return word
            else:
                copy_word = self.suffix(word)
                if len(copy_word) < len(word):
                    word = copy_word
                else:
                    word = self.converter(word)
                    word = self.suffix(word)

        return word

    # Returns the stemmed versions of the given words
    def stem_words(self, list_of_words):
        list_of_stems = list(map(self.stem_word, list_of_words))

        return list_of_stems