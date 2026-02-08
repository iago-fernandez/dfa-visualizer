import os
from typing import Any, Dict
from .dfa import DFA
from .utils import expand_alphabet_range


def parse_dfa_file(filepath: str) -> DFA:
    """
    Parses a DSL configuration file to instantiate a DFA.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Config file not found: {filepath}")

    config: Dict[str, Any] = {
        "alphabet": set(),
        "states": set(),
        "initial_state": None,
        "final_states": set(),
        "transitions": {}
    }

    current_section = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_idx, line in enumerate(f, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue

            # Parse section headers
            if ':' in line and current_section != "TRANSITIONS":
                key, value = [x.strip() for x in line.split(':', 1)]
                key = key.upper()

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

            # Parse transition logic
            if current_section == "TRANSITIONS":
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError(f"Line {line_idx}: Malformed transition. Expected 'src input dest'")

                src, input_def, dest = parts

                try:
                    symbols = expand_alphabet_range(input_def)
                except ValueError as e:
                    raise ValueError(f"Line {line_idx}: {e}")

                for sym in symbols:
                    config["transitions"][(src, sym)] = dest

    # Validation pipeline
    _validate_configuration(config)

    return DFA(
        states=config["states"],
        alphabet=config["alphabet"],
        transitions=config["transitions"],
        initial_state=config["initial_state"],
        final_states=config["final_states"]
    )


def _validate_configuration(config: Dict[str, Any]) -> None:
    """
    Internal validator for DFA logical consistency.
    """
    required_keys = ["alphabet", "states", "initial_state"]
    for key in required_keys:
        if not config.get(key):
            raise ValueError(f"Missing required definition: {key.upper()}")

    if config["initial_state"] not in config["states"]:
        raise ValueError(f"Initial state '{config['initial_state']}' is undefined")

    invalid_finals = config["final_states"] - config["states"]
    if invalid_finals:
        raise ValueError(f"Final states undefined: {invalid_finals}")

    for (src, sym), dest in config["transitions"].items():
        if sym not in config["alphabet"]:
            raise ValueError(f"Transition symbol '{sym}' not in alphabet")
        if src not in config["states"]:
            raise ValueError(f"Transition source '{src}' undefined")
        if dest not in config["states"]:
            raise ValueError(f"Transition destination '{dest}' undefined")