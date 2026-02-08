import sys
import os
import time

# Robust import handling allowing execution as script or module
try:
    from src.loader import parse_dfa_file
    from src.dfa import DFA
    from src.utils import expand_alphabet_range
except ImportError:
    # Fallback for direct script execution without package context
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from src.loader import parse_dfa_file
    from src.dfa import DFA
    from src.utils import expand_alphabet_range


# UI helper functions


def print_header(title: str) -> None:
    """
    Prints a formatted header to the console.
    """
    print(f"\n{'=' * 60}\n {title.upper()}\n{'=' * 60}")


def print_separator() -> None:
    """
    Prints a separator line to the console.
    """
    print("-" * 60)


def get_input(prompt: str) -> str:
    """
    Wraps standard input with a consistent prompt style.
    """
    return input(f" >> {prompt}: ").strip()


# Interactive mode logic


def build_dfa_interactively() -> tuple[DFA, str]:
    """
    Orchestrates the interactive creation of a DFA by querying the user.
    Returns the configured DFA object and a generic model name.
    """
    print_header("Interactive creation mode")
    
    # Configure the alphabet
    print_separator()
    print("Define valid symbols (e.g., 'a-z', '0-1', 'a b c')")
    while True:
        try:
            val = get_input("Alphabet")
            alphabet = expand_alphabet_range(val)
            if not alphabet:
                raise ValueError("Alphabet cannot be empty")
            print(f" -> {len(alphabet)} symbols registered")
            break
        except ValueError as e:
            print(f" [!] Error: {e}")

    # Define the state set
    print_separator()
    while True:
        try:
            count = int(get_input("Number of states"))
            if count > 0:
                states = {f"q{i}" for i in range(count)}
                print(f" -> Generated: {', '.join(sorted(list(states)))}")
                break
            print(" [!] Must be > 0")
        except ValueError:
            print(" [!] Invalid integer")

    # Configure transitions
    print_separator()
    print("Format: src input dest (e.g., 'q0 0 q1'). Type 'done' to finish.")
    transitions = {}
    
    while True:
        entry = get_input("Transition")
        if entry.lower() == 'done':
            break
        
        try:
            parts = entry.split()
            if len(parts) != 3:
                raise ValueError("Invalid format")
            
            src, raw_in, dest = parts
            if src not in states or dest not in states:
                raise ValueError("State not defined")
            
            syms = expand_alphabet_range(raw_in)
            if not syms.issubset(alphabet):
                raise ValueError("Contains symbols outside alphabet")
                
            for s in syms:
                transitions[(src, s)] = dest
                
        except ValueError as e:
            print(f" [!] {e}")

    # Set initial and final states
    print_separator()
    while True:
        init = get_input("Initial state")
        if init in states:
            break
        print(f" [!] State {init} not found")

    while True:
        finals = set(get_input("Final states (space sep)").split())
        if finals.issubset(states):
            break
        print(" [!] Invalid states detected")

    return DFA(states, alphabet, transitions, init, finals), "interactive_model"


# Simulation logic


def run_simulation(dfa: DFA, session_dir: str) -> None:
    """
    Runs the main simulation loop, handling input validation and trace generation.
    """
    print_header("Simulation mode")
    print(f"Valid alphabet: {sorted(list(dfa.alphabet))}")
    
    trace_id = 1
    while True:
        print_separator()
        inp = input(f"[{trace_id}] Input > ").strip()
        
        if inp.lower() == 'exit':
            break
        
        try:
            accepted, path, edges = dfa.validate_string(inp)
            print(f"Result: {'ACCEPTED' if accepted else 'REJECTED'}")
            print(f"Path:   {' -> '.join(path)}")
            
            if get_input("Generate diagram? (y/n)").lower() == 'y':
                clean_name = "".join([c if c.isalnum() else "_" for c in inp])
                out_path = os.path.join(session_dir, f"trace_{clean_name}")
                dfa.visualize(out_path, path, edges)
                print(f" -> Saved to {out_path}.png")
                
            trace_id += 1
        except ValueError as e:
            print(f" [Error] {e}")


# Main execution flow


def main() -> None:
    """
    Entry point for the application. Handles mode selection and session setup.
    """
    print_header("DFA visualizer & runner")
    mode = get_input("Select mode ([1] File, [2] Interactive)")
    
    dfa = None
    name = "model"
    
    try:
        if mode == '1':
            # Dynamic example listing
            ex_dir = os.path.join(os.path.dirname(__file__), 'examples')
            if os.path.exists(ex_dir):
                print("\nAvailable examples:")
                for f in os.listdir(ex_dir):
                    if f.endswith('.txt'):
                        print(f" * {f}")
            print("")
            
            fname = get_input("Filename/path")
            full_path = fname if os.path.exists(fname) else os.path.join(ex_dir, fname)
            dfa = parse_dfa_file(full_path)
            name = os.path.splitext(os.path.basename(fname))[0]
            
        elif mode == '2':
            dfa, name = build_dfa_interactively()
        else:
            print("Invalid selection")
            return

        # Initialize session
        ts = time.strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join("assets", f"session_{ts}_{name}")
        os.makedirs(session_dir, exist_ok=True)
        
        # Export base structure
        if get_input("Export base diagram? (y/n)").lower() == 'y':
            dfa.visualize(os.path.join(session_dir, "base_structure"))

        run_simulation(dfa, session_dir)

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")


if __name__ == "__main__":
    main()