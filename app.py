"""Tianwin Garage Operations Analytics entry point."""

import streamlit as st

from src.data_loader import load_orders
from src.ui import render_app

st.set_page_config(page_title="Tianwin Garage Operations Analytics", page_icon="📊", layout="wide")
st.markdown(
    """<style>
.stApp{background:#F7F8FA;color:#17212B}.block-container{max-width:1280px;padding-top:2rem}.hero{background:white;border:1px solid #E2E8F0;border-left:5px solid #1F5A7A;border-radius:8px;padding:2rem 2.2rem;margin-bottom:1rem}.hero h1{font-size:3rem;margin:.1rem 0}.hero h3{color:#1F5A7A;margin:.2rem 0 1rem}.eyebrow{font-weight:700;letter-spacing:.13em;color:#506273}.badges{font-weight:600;color:#2F7D62;margin-top:1rem}.scope{color:#596878;margin-top:.8rem;font-size:.9rem}.insight{background:white;border:1px solid #E2E8F0;border-radius:7px;padding:1rem;min-height:180px}.insight b{color:#1F5A7A}.insight p{font-size:.92rem}.insight span{font-weight:700}.footer{text-align:center;color:#718096;border-top:1px solid #E2E8F0;margin-top:3rem;padding:2rem}</style>""",
    unsafe_allow_html=True,
)
render_app(load_orders())
