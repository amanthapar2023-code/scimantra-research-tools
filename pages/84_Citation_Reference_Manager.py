"""SciMantra Research OS — Citation & Reference Manager."""
import pandas as pd
import streamlit as st
from src.scimantra.citation_reference_manager import add_reference,audit,bibtex

st.set_page_config(page_title='Citation & Reference Manager',page_icon='📚',layout='wide')
st.title('📚 Citation & Reference Manager')
st.caption('Centralize references, detect likely duplicates, track verification, and export BibTeX.')
st.info('Reference metadata is bibliographic information. Verification does not certify the underlying scientific claim.')
if 'reference_registry' not in st.session_state: st.session_state.reference_registry=[]
reg=st.session_state.reference_registry
with st.expander('➕ Add reference',expanded=True):
    with st.form('ref_form'):
        a,b=st.columns(2); title=a.text_input('Title *'); authors=b.text_input('Authors'); c,d=st.columns(2); year=c.text_input('Year'); journal=d.text_input('Journal'); e,f=st.columns(2); doi=e.text_input('DOI'); source=f.text_input('Source / URL'); ok=st.form_submit_button('Add reference',type='primary')
    if ok:
        try: st.session_state.reference_registry=add_reference(reg,title=title,authors=authors,year=year,journal=journal,doi=doi,source=source); st.success('Reference added.')
        except ValueError as exc: st.error(str(exc))
reg=st.session_state.reference_registry
q=st.text_input('Search references',placeholder='title, author, journal, DOI')
view=[r for r in reg if not q.strip() or q.lower() in ' '.join(str(v) for v in r.values()).lower()]
if view:
    df=pd.DataFrame(view)
    st.dataframe(df,use_container_width=True,hide_index=True)
    ids=[r['id'] for r in view]; chosen=st.selectbox('Reference to verify',ids)
    if st.button('Mark selected as Verified'): 
        for r in reg:
            if r['id']==chosen:r['status']='Verified'
        st.rerun()
else: st.info('No references yet. Add your first DOI or bibliographic record above.')
st.divider(); st.subheader('🔎 Reference audit')
a=audit(reg); x,y,z=st.columns(3); x.metric('References',a['count']); y.metric('Likely duplicates',len(a['duplicates'])); z.metric('Unverified',a['unverified'])
if a['missing_metadata']: st.warning('Missing bibliographic metadata: '+', '.join(a['missing_metadata']))
if a['duplicates']: st.error('Likely duplicate IDs: '+str(a['duplicates']))
st.subheader('Export')
if reg:
    st.download_button('⬇️ Export CSV',pd.DataFrame(reg).to_csv(index=False),'scimantra_references.csv','text/csv')
    st.download_button('⬇️ Export BibTeX',bibtex(reg),'scimantra_references.bib','text/plain')
st.caption('Module 84 · Citation & Reference Manager')
