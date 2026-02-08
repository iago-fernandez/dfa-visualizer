import graphviz
from typing import Optional, Tuple, List, Set, Dict


class DFA:
    """
    Represents a Deterministic Finite Automaton (DFA).
    Optimized for validation speed and structured visualization.
    """
    __slots__ = (
        'states',
        'alphabet',
        'transitions',
        'initial_state',
        'final_states',
        '_grouped_transitions'
    )

    def __init__(self,
                 states: Set[str],
                 alphabet: Set[str],
                 transitions: Dict[Tuple[str, str], str],
                 initial_state: str,
                 final_states: Set[str]):
        """
        Initializes the DFA with immutable sets for O(1) lookups.
        """
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        
        # Pre-compute grouped transitions for faster lookup during visualization
        self._grouped_transitions = self._group_transitions_by_edge()

    def _group_transitions_by_edge(self) -> Dict[Tuple[str, str], List[str]]:
        """
        Groups symbols that share the same source and destination.
        """
        grouped = {}
        for (src, symbol), dest in self.transitions.items():
            key = (src, dest)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(symbol)
        return grouped

    def validate_string(self, input_string: str) -> Tuple[bool, List[str], List[Tuple[str, str, str]]]:
        """
        Processes an input string through the DFA.

        Returns:
            Tuple containing boolean validity, list of visited states, and list of transitions.
        """
        # Validate alphabet adherence
        for char in input_string:
            if char not in self.alphabet:
                raise ValueError(f"Symbol '{char}' not in alphabet")

        current_state = self.initial_state
        path = [current_state]
        edge_path = []

        for symbol in input_string:
            # Direct hash map lookup for O(1) transition resolution
            next_state = self.transitions.get((current_state, symbol))

            if next_state is None:
                # Implicit rejection (dead state)
                return False, path, edge_path

            edge_path.append((current_state, next_state, symbol))
            current_state = next_state
            path.append(current_state)

        return current_state in self.final_states, path, edge_path

    @staticmethod
    def _format_edge_label(symbols: List[str]) -> str:
        """
        Compresses a list of symbols into a readable label using ranges where possible.
        """
        symbols_set = set(symbols)
        parts = []

        import string
        lower = set(string.ascii_lowercase)
        digits = set(string.digits)

        if lower.issubset(symbols_set):
            parts.append("a-z")
            symbols_set -= lower
        if digits.issubset(symbols_set):
            parts.append("0-9")
            symbols_set -= digits

        parts.extend(sorted(list(symbols_set)))
        return ", ".join(parts)

    def visualize(self,
                  filename: str = "dfa_output",
                  path: Optional[List[str]] = None,
                  edge_path: Optional[List[Tuple[str, str, str]]] = None) -> str:
        """
        Renders the DFA using Graphviz.
        """
        dot = graphviz.Digraph(format='png', engine='dot')
        dot.attr(rankdir='LR', dpi='150')

        # Visual configuration
        hl_color = '#006400'
        def_color = 'black'
        hl_width = '2.5'
        def_width = '1.0'

        is_trace = path is not None and len(path) > 0
        
        # Sets for O(1) lookup during rendering loop
        visited_nodes = set(path) if path else set()
        traversed_edges = set(edge_path) if edge_path else set()

        # Draw the start pointer
        start_color = hl_color if is_trace else def_color
        start_width = hl_width if is_trace else def_width
        dot.node('start_pointer', label='', shape='none', width='0', height='0')
        dot.edge('start_pointer', self.initial_state, color=start_color, penwidth=start_width)

        # Draw the nodes
        for state in sorted(list(self.states)):
            is_final = state in self.final_states
            is_visited = state in visited_nodes
            
            dot.node(
                state,
                shape='doublecircle' if is_final else 'circle',
                color=hl_color if is_visited else def_color,
                fontcolor=hl_color if is_visited else def_color,
                penwidth=hl_width if is_visited else def_width
            )

        # Draw the edges using grouped transitions
        for (src, dest), symbols in self._grouped_transitions.items():
            label = self._format_edge_label(symbols)
            
            # Check if this specific aggregate edge was part of the trace
            is_edge_active = False
            if is_trace:
                for sym in symbols:
                    if (src, dest, sym) in traversed_edges:
                        is_edge_active = True
                        break

            dot.edge(
                src, dest, label=label,
                color=hl_color if is_edge_active else def_color,
                fontcolor=hl_color if is_edge_active else def_color,
                penwidth=hl_width if is_edge_active else def_width
            )

        return dot.render(filename, cleanup=True)