import streamlit as st
from pydantic import ValidationError
from ..models.project import Project, Geometry
from ..models.materials import Concrete, PTStrand, Rebar
from ..models.design_state import DesignState


def collect_inputs() -> tuple[Project, Concrete, PTStrand, Rebar, DesignState] | None:
    st.sidebar.header("Project Info")
    name = st.sidebar.text_input("Project name")

    st.header("Geometry")
    span_x = st.number_input("Span X (ft)", min_value=10, value=30)
    span_y = st.number_input("Span Y (ft)", min_value=10, value=30)
    slab_thick = st.number_input("Slab thickness (in)", min_value=5.0, value=7.0)
    max_beam_depth = st.number_input("Max beam depth (in)", min_value=10.0, value=24.0)

    st.header("Materials & Costs")
    fc = st.number_input("Concrete f'c (psi)", min_value=5000, max_value=22000, value=6000)
    conc_price = st.number_input("Concrete unit cost $/yd3", min_value=1.0, value=250.0)
    strand_cost = st.number_input("PT strand cost $/lb", min_value=1.0, value=1.5)
    rebar_cost = st.number_input("Rebar cost $/lb", min_value=1.0, value=0.9)

    st.header("Initial Design State")
    P_avg = st.number_input("Average prestress (psi)", min_value=100, value=150)
    rho = st.number_input("Rebar ratio", min_value=0.001, value=0.003, step=0.0005)

    if not st.button("Run Solver"):
        return None

    try:
        geom = Geometry(span_x=span_x, span_y=span_y, slab_thick=slab_thick, max_beam_depth=max_beam_depth)
        project = Project(name=name, geometry=geom)
        concrete = Concrete(fc=fc, unit_cost=conc_price)
        strand = PTStrand(unit_cost=strand_cost)
        rebar = Rebar(unit_cost=rebar_cost)
        base_state = DesignState(fc=fc, P_avg=P_avg, rho=rho, slab_thick=slab_thick, beam_depth=max_beam_depth)
    except ValidationError as e:
        st.error(f"Input error: {e}")
        return None
    return project, concrete, strand, rebar, base_state
