import streamlit as st
from ..solver.scorer import ScoredDesign


def show_results(results: list[ScoredDesign]):
    if not results:
        st.write("No feasible designs.")
        return
    data = [{
        "h": r.state.slab_thick,
        "fc": r.state.fc,
        "P_avg": r.state.P_avg,
        "rho": r.state.rho,
        "cost": r.cost,
    } for r in results]
    st.dataframe(data)
