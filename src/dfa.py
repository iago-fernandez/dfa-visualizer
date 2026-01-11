import graphviz
from typing import Optional


class DFA:
    def __init__(self,
                 states: set[str],
                 alphabet: set[str],
                 transitions: dict[tuple[str, str], str],
                 initial_state: str,
                 final_states: set[str]):
        """
        Initialize the Deterministic Finite Automaton components.

        :param states: Set of states in the automaton.
        :param alphabet: Set of allowed symbols.
        :param transitions: Dictionary mapping (state, symbol) to next_state.
        :param initial_state: The starting state.
        :param final_states: Set of accepting states.
        """
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

    def validate_string(self, input_string: str) -> tuple[bool, list[str], list[tuple[str, str, str]]]:
        """
        Validates the input string and returns the acceptance status along with the execution path.

        :param input_string: The string to process.
        :return: Tuple containing (is_accepted, state_path, transition_path).
        """
        # Ensure strict alphabet validation
        if not all(char in self.alphabet for char in input_string):
            raise ValueError("Input string contains symbols not present in the alphabet")

        current_state = self.initial_state
        path = [current_state]
        edge_path = []

        for symbol in input_string:
            next_state = self.transitions.get((current_state, symbol))
            if next_state is None:
                # Transition not defined implies rejection in strict DFA definitions
                return False, path, edge_path

            edge_path.append((current_state, next_state, symbol))
            current_state = next_state
            path.append(current_state)

        is_accepted = current_state in self.final_states
        return is_accepted, path, edge_path

    def visualize(self,
                  filename: str = "dfa_output",
                  path: Optional[list[str]] = None,
                  edge_path: Optional[list[tuple[str, str, str]]] = None) -> str:
        """
        Generates a Graphviz representation of the DFA.
        Highlights the execution path if provided.

        :param filename: Base name for the output file (without extension).
        :param path: List of visited states to highlight.
        :param edge_path: List of traversed edges to highlight.
        :return: The path to the rendered file.
        """
        dot = graphviz.Digraph(format='png', engine='dot')
        dot.attr(rankdir='LR')

        # Style constants for visualization
        highlight_color = 'darkgreen'
        default_color = 'black'

        # Determine if we are visualizing a trace or just the structure
        is_trace_active = path is not None

        # Start Arrow: only highlight if we are tracing an input, otherwise keep it standard black
        start_color = highlight_color if is_trace_active else default_color
        start_penwidth = '2.0' if is_trace_active else '1.0'

        dot.node('start', label='', shape='none', width='0', height='0')
        dot.edge('start', self.initial_state, color=start_color, penwidth=start_penwidth)

        visited_nodes = set(path) if path else set()
        visited_edges = set(edge_path) if edge_path else set()

        # States
        for state in sorted(list(self.states)):
            shape = 'doublecircle' if state in self.final_states else 'circle'

            # Determine styling based on visitation
            if state in visited_nodes:
                color = highlight_color
                font_color = highlight_color
                penwidth = '2.0'
            else:
                color = default_color
                font_color = default_color
                penwidth = '1.0'

            dot.node(state, shape=shape, color=color, fontcolor=font_color, penwidth=penwidth)

        # Transitions
        for (src, symbol), dest in self.transitions.items():
            # Check if this specific transition was traversed
            is_used = (src, dest, symbol) in visited_edges

            if is_used:
                edge_color = highlight_color
                label_font_color = highlight_color
                edge_penwidth = '2.0'
            else:
                edge_color = default_color
                label_font_color = default_color
                edge_penwidth = '1.0'

            dot.edge(src, dest, label=symbol,
                     color=edge_color,
                     fontcolor=label_font_color,
                     penwidth=edge_penwidth)

        # Render and cleanup source file
        return dot.render(filename, cleanup=True)