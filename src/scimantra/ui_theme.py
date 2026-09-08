"""Shared responsive visual polish for the Streamlit app."""
import streamlit as st


def apply() -> None:
    st.markdown("""
    <style>
    .block-container{max-width:1450px;padding-top:1.2rem;padding-bottom:3rem}
    .hero{padding:2rem 2.2rem;border-radius:22px;background:linear-gradient(135deg,#e9f4ff 0%,#f8fbff 55%,#eefaf5 100%);border:1px solid #d8e8f5;margin-bottom:1.3rem;box-shadow:0 6px 24px rgba(20,55,80,.06)}
    .hero h1{margin:0;color:#0b2033;font-size:2.55rem;font-weight:750}.hero p{margin:.5rem 0 0;color:#486176;font-size:1.08rem}
    .eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#2574a8;margin-bottom:.35rem}
    .section-title{font-size:1.45rem;font-weight:700;color:#102b40;margin:1.1rem 0 .7rem}
    .tool-card{border:1px solid #dfe8ee;border-radius:16px;padding:1.05rem 1.1rem;background:#fff;min-height:132px;margin-bottom:.9rem;box-shadow:0 3px 12px rgba(20,55,80,.045)}
    .tool-card h3{margin:0 0 .35rem;color:#17344a;font-size:1.12rem}.tool-card p{margin:0;color:#536b7b;line-height:1.5}.pro-card{background:linear-gradient(135deg,#fffdf5,#fff);border-color:#ead9a5}
    .flow-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
    .flow{border:1px solid #dfe8ee;border-radius:14px;padding:1rem;text-align:center;background:#fff;min-height:92px;display:flex;flex-direction:column;justify-content:center;box-sizing:border-box}.flow strong{display:block;color:#18364b}.flow span{font-size:.86rem;color:#637889}
    @media(max-width:1100px){.flow-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
    @media(max-width:700px){.block-container{padding-left:.8rem;padding-right:.8rem}.hero{padding:1.35rem}.hero h1{font-size:2rem}.hero p{font-size:.98rem}.flow-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.flow{min-height:78px;padding:.7rem}.section-title{font-size:1.25rem}}
    </style>
    """, unsafe_allow_html=True)
