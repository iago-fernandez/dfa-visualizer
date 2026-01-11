import os
from typing import Any

from .dfa import DFA
from .utils import expand_alphabet_range


def parse_dfa_file(filepath: str) -> DFA:
    """
    Parses a formatted text file to construct a DFA instance.

    File Format Structure (see examples/ for further details and use cases):
    ----------------------
    # Comments are allowed
    ALPHABET: 0-1
    STATES: q0 q1 q2
    INITIAL_STATE: q0
    FINAL_STATES: q2
    TRANSITIONS:
    q0 0 q0
    q0 1 q1
    ...
    ----------------------

    :param filepath: Path to the DFA configuration file.
    :return: A configured DFA instance.
    :raises ValueError: If the file format is invalid or missing sections.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Configuration file not found: {filepath}")

    # Explicitly type the dictionary to allow mixed value types (sets, strings, dicts)
    config: dict[str, Any] = {
        "alphabet": None,
        "states": None,
        "initial_state": None,
        "final_states": None,
        "transitions": {}
    }

    current_section = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Detect sections
            if ':' in line and current_section != "TRANSITIONS":
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()

                if key == "ALPHABET":
                    config["alphabet"] = expand_alphabet_range(value)
                elif key == "STATES":
                    config["states"] = set(value.split())
                elif key == "INITIAL_STATE":
                    config["initial_state"] = value
                elif key == "FINAL_STATES":
                    config["final_states"] = set(value.split())
                elif key == "TRANSITIONS":
                    current_section = "TRANSITIONS"
                continue

            # Process transitions section
            if current_section == "TRANSITIONS":
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError(f"Line {line_num}: Invalid transition format. Expected 'src input dest'")

                source, input_symbol, destination = parts

                # Expand input ranges in transitions (e.g., 'q0 a-z q1')
                try:
                    symbols = expand_alphabet_range(input_symbol)
                except ValueError as e:
                    raise ValueError(f"Line {line_num}: {e}")

                for sym in symbols:
                    config["transitions"][(source, sym)] = destination

    # Validation
    if not config["alphabet"]:
        raise ValueError("Missing ALPHABET definition")
    if not config["states"]:
        raise ValueError("Missing STATES definition")
    if not config["initial_state"]:
        raise ValueError("Missing INITIAL_STATE definition")
    if not config["final_states"]:
        # It is technically possible to have no final states
        config["final_states"] = set()

    # Validate state existence
    if config["initial_state"] not in config["states"]:
        raise ValueError(f"Initial state '{config['initial_state']}' is not in defined states")

    invalid_final = config["final_states"] - config["states"]
    if invalid_final:
        raise ValueError(f"Final states {invalid_final} are not in defined states")

    # Validate transition symbols
    for (source, sym), destination in config["transitions"].items():
        if sym not in config["alphabet"]:
            raise ValueError(f"Transition symbol '{sym}' not in alphabet")
        if source not in config["states"]:
            raise ValueError(f"Transition source '{source}' invalid")
        if destination not in config["states"]:
            raise ValueError(f"Transition destination '{destination}' invalid")

    return DFA(
        states=config["states"],
        alphabet=config["alphabet"],
        transitions=config["transitions"],
        initial_state=config["initial_state"],
        final_states=config["final_states"]
    )