def expand_alphabet_range(input_str: str) -> set[str]:
    """
    Parses a string containing characters and ranges (e.g., "a-z, 0-9, _")
    and returns a complete set of individual characters.

    Supported patterns:
    * Single characters: "a", "b", "@"
    * Ranges: "a-z", "A-Z", "0-9"
    * Separators: Commas or spaces are treated as delimiters.

    :param input_str: The raw input string from the user.
    :return: A set of unique characters expanded from the input.
    """
    result = set()

    # Normalize separators: replace commas with spaces and split
    parts = input_str.replace(',', ' ').split()

    for part in parts:
        if len(part) == 3 and part[1] == '-':
            # Handle range logic (e.g., "a-z")
            start_char = part[0]
            end_char = part[2]

            # Validation for logical ranges
            if ord(start_char) > ord(end_char):
                raise ValueError(f"Invalid range: {part} (Start > End)")

            # Expand range using ASCII values
            expanded = {chr(c) for c in range(ord(start_char), ord(end_char) + 1)}
            result.update(expanded)
        else:
            # Handle individual characters (e.g., "_")
            result.update(set(part))

    return result