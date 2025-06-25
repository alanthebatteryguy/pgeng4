import streamlit as st
from .ui.input_forms import collect_inputs
from .ui.results import show_results
from .solver.optimize import optimise


def main():
    st.title("Parking Garage Optimiser")
    data = collect_inputs()
    if not data:
        return
    project, concrete, strand, rebar, base_state = data
    results = optimise(project.geometry, base_state, (concrete, strand, rebar))
    show_results(results)


if __name__ == "__main__":
    main()
