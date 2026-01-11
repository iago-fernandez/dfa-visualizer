# DFA Visualizer

A modular Python implementation of **Deterministic Finite Automata (DFA)** designed for logic validation and educational visualization. The tool generates real-time synchronized representations of automaton structures and execution paths using **Graphviz**.

Beyond simple validation, this project serves as:
* A formal implementation of **Automata Theory** concepts.
* A visualization tool for **computational flow analysis**.
* An example of clean architecture in Python, emphasizing separation between logic and rendering.

---

## Mathematical Background

A DFA is formally defined as a 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$:

* $Q$: Finite set of states.
* $\Sigma$: Finite set of symbols (alphabet).
* $\delta: Q \times \Sigma \rightarrow Q$: Transition function.
* $q_0 \in Q$: Initial state.
* $F \subseteq Q$: Set of final (accepting) states.

---

## Features

* **Core Engine**: Robust DFA simulation with alphabet validation.
* **Static View**: High-quality vector rendering of the automaton's topology.
* **Trace View**: Dynamic highlighting of execution paths for specific input strings (forestgreen highlighting for active states and transitions).
* **Clean Output**: Automatic cleanup of Graphviz intermediate files.

---

## Requirements

### System Dependencies

This project requires the **Graphviz binary** to be installed and accessible in the system PATH:

* **Windows**: Download from [graphviz.org](https://graphviz.org/download/). (Select "Add Graphviz to system PATH").
* **Linux**: `sudo apt install graphviz`
* **macOS**: `brew install graphviz`

### Python Dependencies

* Python 3.8+
* graphviz (Python wrapper)

---

## Setup

1. **Clone the repository**:

  ```bash
  git clone <repository-url>
  cd dfa-visualizer
  ```

2. **Environment**:

  ```bash
  python -m venv venv
  # Windows
  .\venv\Scripts\activate
  # Linux/macOS
  source venv/bin/activate
  ```

3. **Install**:

  ```bash
  pip install -r requirements.txt
  ```

---

## Usage

The library is designed to be imported as a module. A typical implementation involves defining the 5-tuple components and invoking the `visualize` method.

* **Static Rendering**: Call `visualize(filename)` to generate the base structure.
* **Trace View**: Pass the `path` and `edge_path` returned by `validate_string()` to highlight the transitions in forestgreen.

Examples of binary multiples and other classic automata will be added to the `examples/` directory soon.
