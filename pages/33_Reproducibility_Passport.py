import streamlit as st
import pandas as pd

st.set_page_config(page_title="Reproducibility Passport | SciMantra", page_icon="🧾", layout="wide")
st.title("🧾 Reproducibility Passport")
st.caption("A pre-submission audit trail for methods, data, analysis and reporting.")

sections={
"Research identity":["Research question is explicitly defined","Primary hypothesis/objective is stated","Study population/system/material is specified","Inclusion/exclusion criteria are recorded"],
"Experimental design":["Controls are defined","Independent biological/experimental replicates are defined","Randomization or allocation procedure is recorded where applicable","Sample-size rationale/power analysis is recorded","Primary endpoint is predefined","Potential confounders are documented"],
"Methods & materials":["Protocol/version is archived","Critical reagents/materials and sources are recorded","Instrument/model/settings are recorded","Environmental/operational conditions are recorded","Deviations from protocol are logged"],
"Data & analysis":["Raw data are preserved","Data dictionary/units are defined","Missing-data handling is documented","Outlier handling is predefined or transparently reported","Statistical tests match the design","Assumption checks are recorded","Code/calculation workflow is reproducible"],
"Manuscript claims":["Every major claim has supporting evidence","Figures trace back to source data","Numerical values can be traced to analysis outputs","Limitations are explicitly reported","No fabricated or unsupported results are present"],
}
checks=[]
for section,items in sections.items():
    st.subheader(section)
    cols=st.columns(2)
    for i,item in enumerate(items):
        ok=cols[i%2].checkbox(item,key="rp_"+str(abs(hash(section+item))))
        checks.append(ok)
score=round(100*sum(checks)/len(checks)) if checks else 0
st.divider(); st.metric("Reproducibility readiness",f"{score}%")
if score<60: st.error("High reproducibility debt — resolve core documentation and design gaps before submission.")
elif score<85: st.warning("Moderate reproducibility debt — strengthen the missing items.")
else: st.success("Strong readiness — still verify every item against the actual study record.")
report=pd.DataFrame({"Item":[x for items in sections.values() for x in items],"Complete":checks})
st.download_button("⬇️ Export audit",report.to_csv(index=False).encode(),"scimantra_reproducibility_passport.csv","text/csv")
