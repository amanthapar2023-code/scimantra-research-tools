from __future__ import annotations

import io
from typing import Optional

import pandas as pd
import streamlit as st

KEY_DF = "scimantra_research_df"
KEY_NAME = "scimantra_research_filename"
KEY_SHEET = "scimantra_research_sheet"


def store_dataframe(df: pd.DataFrame, filename: str, sheet: Optional[str] = None) -> None:
    st.session_state[KEY_DF] = df.copy()
    st.session_state[KEY_NAME] = filename
    st.session_state[KEY_SHEET] = sheet


def get_dataframe() -> Optional[pd.DataFrame]:
    df = st.session_state.get(KEY_DF)
    return df.copy() if isinstance(df, pd.DataFrame) else None


def metadata() -> dict:
    df = get_dataframe()
    return {
        "filename": st.session_state.get(KEY_NAME, ""),
        "sheet": st.session_state.get(KEY_SHEET),
        "rows": int(len(df)) if df is not None else 0,
        "columns": int(len(df.columns)) if df is not None else 0,
    }


def excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return buf.getvalue()


def clear() -> None:
    for key in (KEY_DF, KEY_NAME, KEY_SHEET):
        st.session_state.pop(key, None)
