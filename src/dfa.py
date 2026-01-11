import graphviz
from typing import Set, Dict, Tuple, List, Optional

class DFA:
    def __init__(self,
                 states: Set[str],
                 alphabet: Set[str],
                 transitions: Dict[Tuple[str, str], str],
                 initial_state: str,
                 final_states: Set[str]):
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

    def validate_string(self, input_string: str) -> Tuple[bool, List[str], List[Tuple[str, str, str]]]:
        """
        Validates the input string and returns the acceptance status along with the execution path.

        :param input_string: The string to process.
        :return: Tuple containing (is_accepted, state_path, transition_path).
        """
        # Ensure strict alphabet validation
        if not all(char in self.alphabet for char in input_string):
            raise ValueError("Input string contains symbols not present in the alphabet.")

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
                  path: Optional[List[str]] = None,
                  edge_path: Optional[List[Tuple[str, str, str]]] = None) -> str:
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

        # Invisible start node to point to the initial state
        dot.node('start', label='', shape='none', width='0', height='0')
        dot.edge('start', self.initial_state)

        visited_nodes = set(path) if path else set()
        visited_edges = set(edge_path) if edge_path else set()

        for state in self.states:
            shape = 'doublecircle' if state in self.final_states else 'circle'

            # Highlight logic: Forestgreen for active path, black for standard
            color = 'forestgreen' if state in visited_nodes else 'black'
            penwidth = '2.0' if state in visited_nodes else '1.0'

            dot.node(state, shape=shape, color=color, penwidth=penwidth)

        for (src, symbol), dest in self.transitions.items():
            # Check if specific transition was used in the trace
            is_used = (src, dest, symbol) in visited_edges

            color = 'forestgreen' if is_used else 'black'
            style = 'bold' if is_used else 'solid'

            dot.edge(src, dest, label=symbol, color=color, style=style)

        # Renders the graph to a file and returns the file path
        return dot.render(filename, cleanup=True)