from collections import defaultdict
import re

# Global variable
_SYN_MAP_CACHE = None

def load_synonyms(file_path="../synonyms.txt"):
    """Loads synonyms from a file only once and caches them."""
    global _SYN_MAP_CACHE
    # Return cached version if already loaded
    if _SYN_MAP_CACHE is not None:
        return _SYN_MAP_CACHE
    
    synonym_map = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if "→" in line:
                canonical, synonyms = map(str.strip, line.split("→"))
                for synonym in map(str.strip, synonyms.split(",")):
                    synonym_map[synonym.lower()] = canonical.lower()
    
    _SYN_MAP_CACHE = synonym_map  # Cache the loaded synonyms
    return _SYN_MAP_CACHE

SYNONYM_MAP = load_synonyms()
