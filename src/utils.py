from typing import Set


def expand_alphabet_range(input_str: str) -> Set[str]:
    """
    Parses a string definition of an alphabet into a set of characters.
    Handles ranges, individual characters, and separators.
    """
    result = set()
    
    # Standardize separators to spaces to handle various input formats
    normalized = input_str.replace(',', ' ')
    parts = normalized.split()

    for part in parts:
        if len(part) == 3 and part[1] == '-':
            start, end = part[0], part[2]
            
            if ord(start) > ord(end):
                raise ValueError(f"Invalid ASCII range: {part}")
            
            # Efficient range generation
            result.update(chr(c) for c in range(ord(start), ord(end) + 1))
        else:
            # Handle literals
            result.update(part)

    return result