import graphviz
from typing import Optional
import string


class DFA:
    """
    Represents a Deterministic Finite Automaton (DFA).
    Handles validation of strings and visualization of the automaton structure.
    """

    def __init__(self,
                 states: set[str],
                 alphabet: set[str],
                 transitions: dict[tuple[str, str], str],
                 initial_state: str,
                 final_states: set[str]):
        """
        Initialize the Deterministic Finite Automaton components.

        :param states: Set of all states in the automaton.
        :param alphabet: Set of allowed input symbols.
        :param transitions: Dictionary mapping (source_state, input_symbol) to destination_state.
        :param initial_state: The starting state of the automaton.
        :param final_states: Set of states where acceptance occurs.
        """
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

    def validate_string(self, input_string: str) -> tuple[bool, list[str], list[tuple[str, str, str]]]:
        """
        Validates the input string against the DFA's rules and returns the execution trace.

        :param input_string: The string to process.
        :return: A tuple containing:
                 - bool: True if accepted, False otherwise.
                 - list[str]: The sequence of states visited (the path).
                 - list[tuple[str, str, str]]: The sequence of specific transitions taken (src, dest, symbol).
        :raises ValueError: If input string contains symbols not in the alphabet.
        """
        # Ensure strict alphabet validation before processing
        if not all(char in self.alphabet for char in input_string):
            invalid_chars = [c for c in input_string if c not in self.alphabet]
            raise ValueError(f"Input string contains symbols not in the alphabet: {set(invalid_chars)}")

        current_state = self.initial_state
        # Path tracks states visited: [q0, q1, q2...]
        path = [current_state]
        # Edge path tracks specific transitions taken: [(q0, q1, 'a'), (q1, q2, 'b')...]
        edge_path = []

        for symbol in input_string:
            # In a strict DFA, every state must have a transition for every symbol
            # Using .get() handles implicit rejection (dead states) if definitions are incomplete
            next_state = self.transitions.get((current_state, symbol))

            if next_state is None:
                # Transition not defined implies immediate rejection
                return False, path, edge_path

            edge_path.append((current_state, next_state, symbol))
            current_state = next_state
            path.append(current_state)

        # Determine acceptance based on the final state reached
        is_accepted = current_state in self.final_states
        return is_accepted, path, edge_path

    @staticmethod
    def _format_edge_label(symbols: list[str]) -> str:
        """
        Helper to compress a list of edge symbols into a readable label.
        Detects common ranges like a-z or 0-9.
        """
        symbols_set = set(symbols)
        parts = []

        # Pre-defined common ranges to detect
        lowercase = set(string.ascii_lowercase)
        digits = set(string.digits)

        # Check for complete ranges
        if lowercase.issubset(symbols_set):
            parts.append("a-z")
            symbols_set -= lowercase
        if digits.issubset(symbols_set):
            parts.append("0-9")
            symbols_set -= digits

        # Add remaining individual symbols, sorted for consistency
        for sym in sorted(list(symbols_set)):
            parts.append(sym)

        return ", ".join(parts)

    def visualize(self,
                  filename: str = "dfa_output",
                  path: Optional[list[str]] = None,
                  edge_path: Optional[list[tuple[str, str, str]]] = None) -> str:
        """
        Generates a Graphviz representation of the DFA, grouping transitions between states.
        Highlights the execution path if a trace is provided.

        :param filename: Base name for the output file (without extension).
        :param path: Optional list of visited states to highlight during a trace.
        :param edge_path: Optional list of specific transitions taken during a trace.
        :return: The absolute path to the rendered image file.
        """
        dot = graphviz.Digraph(format='png', engine='dot')
        # LR = Left to Right layout, usually cleaner for DFAs
        dot.attr(rankdir='LR')

        # Style constants for visualization
        highlight_color = '#006400'  # Dark green for active traces
        default_color = 'black'
        highlight_penwidth = '2.5'
        default_penwidth = '1.0'

        # Determine if we are visualizing an active trace
        is_trace_active = path is not None and len(path) > 0

        # 1. Draw Start Arrow
        # Only highlight the start arrow if it's part of an active trace
        start_color = highlight_color if is_trace_active else default_color
        start_penwidth = highlight_penwidth if is_trace_active else default_penwidth

        dot.node('start_pointer', label='', shape='none', width='0', height='0')
        dot.edge('start_pointer', self.initial_state, color=start_color, penwidth=start_penwidth)

        # Optimization sets for quick lookups
        visited_nodes = set(path) if path else set()
        traversed_edges_specific = set(edge_path) if edge_path else set()

        # 2. Draw States (Nodes)
        # Sort states to ensure consistent output orientation
        sorted_states = sorted(list(self.states), key=lambda s: (len(s), s))
        for state in sorted_states:
            # Final states are double circles
            shape = 'doublecircle' if state in self.final_states else 'circle'

            # Determine styling based on visitation in trace
            if state in visited_nodes:
                color = highlight_color
                font_color = highlight_color
                penwidth = highlight_penwidth
            else:
                color = default_color
                font_color = default_color
                penwidth = default_penwidth

            dot.node(state, shape=shape, color=color, fontcolor=font_color, penwidth=penwidth)

        # 3. Group Transitions
        # Group symbols by shared (source, destination) pairs
        # Structure: {(src, dest): [symbol1, symbol2, ...]}
        grouped_transitions: dict[tuple[str, str], list[str]] = {}
        for (src, symbol), dest in self.transitions.items():
            if (src, dest) not in grouped_transitions:
                grouped_transitions[(src, dest)] = []
            grouped_transitions[(src, dest)].append(symbol)

        # 4. Draw Transitions (Edges)
        for (src, dest), symbols in grouped_transitions.items():
            # Format the label (e.g., "a-z, 0-9")
            label = self._format_edge_label(symbols)

            # Check if ANY symbol in this grouped edge was used in the trace
            is_grouped_edge_used = False
            if is_trace_active:
                for sym in symbols:
                    if (src, dest, sym) in traversed_edges_specific:
                        is_grouped_edge_used = True
                        break

            # Determine styling for the grouped edge
            if is_grouped_edge_used:
                edge_color = highlight_color
                label_font_color = highlight_color
                edge_penwidth = highlight_penwidth
            else:
                edge_color = default_color
                label_font_color = default_color
                edge_penwidth = default_penwidth

            dot.edge(src, dest, label=label,
                     color=edge_color,
                     fontcolor=label_font_color,
                     penwidth=edge_penwidth)

        # Render the graph and return the file path. Cleanup deletes the source .dot file
        return dot.render(filename, cleanup=True)