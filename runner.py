import sys
import os
import time

# Add project root to path to allow importing src modules
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

try:
    from src.loader import parse_dfa_file
    from src.dfa import DFA
    from src.utils import expand_alphabet_range
except ImportError:
    print("[ERROR] Could not import 'src'. Ensure you are running from the project root")
    sys.exit(1)


# UI helper functions


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title.upper()}")
    print("=" * 60)


def print_separator():
    print("-" * 60)


def get_positive_integer(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if value > 0:
                return value
            print("  [!] Please enter a number greater than 0")
        except ValueError:
            print("  [!] Invalid input. Please enter an integer")


# Interactive mode functions


def prompt_alphabet() -> set[str] | None:
    print_separator()
    print("1: Define alphabet")
    print("  Examples: '0-1', 'a-z', 'a b c'")

    while True:
        raw_input = input("  >> Alphabet: ").strip()
        if not raw_input:
            print("  [!] Alphabet cannot be empty")
            continue

        try:
            alphabet = expand_alphabet_range(raw_input)
            print(f"  -> Alphabet set ({len(alphabet)} symbols): {sorted(list(alphabet))}")
            return alphabet
        except ValueError as e:
            print(f"  [!] Error parsing alphabet: {e}")


def prompt_states() -> set[str]:
    print_separator()
    print("2: Define states")
    count = get_positive_integer("  >> Number of states (N): ")
    states = {f"q{i}" for i in range(count)}

    display_states = sorted(list(states), key=lambda x: int(x[1:]))
    print(f"  -> Generated states: {', '.join(display_states)}")
    return states


def prompt_transitions(states: set[str], alphabet: set[str]) -> dict[tuple[str, str], str]:
    print_separator()
    print("4: Define transitions")
    print("  Format: source input target (e.g., 'q0 0 q1')")
    print("  Type 'done' to finish")

    transitions = {}

    while True:
        entry = input("  >> Transition: ").strip()
        if entry.lower() == 'done':
            break

        parts = entry.split()
        if len(parts) != 3:
            print("  [!] Invalid format. Expected: <Source> <Input> <Target>")
            continue

        src, raw_input, dest = parts[0], parts[1], parts[2]

        if src not in states:
            print(f"  [!] Source state '{src}' invalid")
            continue
        if dest not in states:
            print(f"  [!] Target state '{dest}' invalid")
            continue

        try:
            symbols = expand_alphabet_range(raw_input)
            invalid_syms = symbols - alphabet
            if invalid_syms:
                print(f"  [!] Symbols {invalid_syms} not in alphabet")
                continue

            for sym in symbols:
                transitions[(src, sym)] = dest

        except ValueError as e:
            print(f"  [!] Error parsing input range: {e}")

    return transitions


def build_dfa_interactively() -> tuple[DFA, str]:
    """
    Orchestrates the interactive creation of a DFA.
    Returns the DFA object and a suggested name for the session.
    """
    print_header("Interactive creation mode")

    alphabet = prompt_alphabet()
    states = prompt_states()

    print_separator()
    print("3: Initial and final states")
    while True:
        initial_state = input("  >> Initial state: ").strip()
        if initial_state in states:
            break
        print(f"  [!] State '{initial_state}' is not valid")

    while True:
        final_input = input("  >> Final states (space separated): ").strip().split()
        final_states = set(final_input)
        if final_states.issubset(states):
            break
        print("  [!] One or more states are invalid")

    transitions = prompt_transitions(states, alphabet)

    dfa = DFA(states, alphabet, transitions, initial_state, final_states)
    return dfa, "interactive_model"


# File loading mode


def load_dfa_from_file() -> tuple[DFA, str]:
    """
    Handles file selection and parsing.
    Returns the DFA object and the filename for session naming.
    """
    print_header("File loading mode")

    examples_dir = os.path.join(PROJECT_ROOT, 'examples')
    if os.path.exists(examples_dir):
        print("Available example files:")
        files = [f for f in os.listdir(examples_dir) if f.endswith('.txt')]
        for f in files:
            print(f" - {f}")

    print_separator()
    user_input = input(">> Enter filename (from examples) or full path: ").strip()

    # Logic to resolve path
    if os.path.exists(user_input):
        filepath = user_input
    elif os.path.exists(os.path.join(examples_dir, user_input)):
        filepath = os.path.join(examples_dir, user_input)
    else:
        raise FileNotFoundError(f"File not found: {user_input}")

    dfa = parse_dfa_file(filepath)
    model_name = os.path.splitext(os.path.basename(filepath))[0]
    return dfa, model_name


# Main execution flow


def main():
    print_header("DFA Simulation Runner")
    print("Select mode:")
    print(" [1] Load from file")
    print(" [2] Create manually (interactive)")

    while True:
        mode = input("\n>> Select option (1/2): ").strip()
        if mode == '1':
            try:
                dfa, model_name = load_dfa_from_file()
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                return
        elif mode == '2':
            try:
                dfa, model_name = build_dfa_interactively()
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                return
        else:
            print("Invalid option")

    print("\n-> DFA loaded/created successfully")

    # Session setup
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    session_folder_name = f"session_{timestamp}"

    session_dir = os.path.join(PROJECT_ROOT, "assets", session_folder_name)
    os.makedirs(session_dir, exist_ok=True)

    print(f"-> Session directory: assets/{session_folder_name}")

    # Initial visualization
    print_separator()
    gen_initial = input(">> Export full DFA structure diagram now? (y/n): ").strip().lower()
    if gen_initial == 'y':
        filename = os.path.join(session_dir, "dfa_diagram")
        try:
            path = dfa.visualize(filename, path=None, edge_path=None)
            print(f"-> Saved: {path}")
        except Exception as e:
            print(f"[ERROR] Failed to generate initial diagram: {e}")

    # Simulation loop
    print_header("Simulation mode")
    print(f"Alphabet: {sorted(list(dfa.alphabet))}")
    print("Type 'exit' to quit")

    trace_count = 1

    while True:
        print_separator()
        test_str = input(f"[{trace_count}] Input string > ").strip()

        if test_str.lower() == 'exit':
            break

        if not all(c in dfa.alphabet for c in test_str):
            print("[Warning] Input contains symbols not in the defined alphabet")
            continue

        is_accepted, path, edges = dfa.validate_string(test_str)
        status = "ACCEPTED" if is_accepted else "REJECTED"

        print(f"Result: {status}")
        print(f"Trace:  {' -> '.join(path)}")

        gen_trace = input(">> Generate diagram for this trace? (y/n): ").lower()
        if gen_trace == 'y':
            safe_input = "".join([c if c.isalnum() else "_" for c in test_str])
            fname = f"trace_{safe_input}"
            full_path = os.path.join(session_dir, fname)

            try:
                saved_file = dfa.visualize(full_path, path, edges)
                print(f"-> Diagram saved: {saved_file}")
            except Exception as e:
                print(f"[ERROR] Failed to generate diagram: {e}")

            trace_count += 1

    print("\nExiting runner...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")