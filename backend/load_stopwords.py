def load_stopwords(file_path):
    with open(file_path, 'r') as f:
        return set(f.read().splitlines())

# Usage
STOP_WORDS = load_stopwords("../stop_words.txt")

