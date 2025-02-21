from collections import defaultdict
import re

def load_synonyms(file_path):
    synonym_map = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if "→" in line:  # Identify synonym mappings
                canonical, synonyms = map(str.strip, line.split("→"))
                for synonym in map(str.strip, synonyms.split(",")):
                    synonym_map[synonym.lower()] = canonical.lower()  # Normalize to lowercase
    return synonym_map

# Usage
SYNONYM_MAP = load_synonyms("../synonyms.txt")

# Example normalization
text = "Mostly cooked Leaf mustard and Umami powder on a Sauté pan!"
for synonym, canonical in SYNONYM_MAP.items():
    text = re.sub(r'\b' + re.escape(synonym) + r'\b', canonical, text, flags=re.IGNORECASE) # Returns "medium-well mustard greens and msg on a pan!"
print(text)
