"""Central citation/reference registry for SciMantra."""
from __future__ import annotations
import re
from typing import Any

def _key(x: dict[str, Any]) -> str:
    doi=str(x.get('doi','')).strip().lower()
    return 'doi:'+doi if doi else 'title:'+re.sub(r'[^a-z0-9]+',' ',str(x.get('title','')).lower()).strip()

def add_reference(registry:list[dict[str,Any]], *, title:str, authors:str='', year:str='', journal:str='', doi:str='', source:str='') -> list[dict[str,Any]]:
    item={'id':f'REF-{len(registry)+1:05d}','title':title.strip(),'authors':authors.strip(),'year':str(year).strip(),'journal':journal.strip(),'doi':doi.strip(),'source':source.strip(),'status':'Unverified'}
    if not item['title']: raise ValueError('Reference title is required.')
    if any(_key(r)==_key(item) for r in registry): raise ValueError('A likely duplicate reference already exists.')
    registry.append(item); return registry

def audit(registry:list[dict[str,Any]]) -> dict[str,Any]:
    seen={}; duplicates=[]; missing=[]
    for r in registry:
        k=_key(r)
        if k in seen: duplicates.append((seen[k],r.get('id')))
        else: seen[k]=r.get('id')
        if not r.get('title') or (not r.get('doi') and not r.get('journal')): missing.append(r.get('id'))
    return {'count':len(registry),'duplicates':duplicates,'missing_metadata':missing,'unverified':sum(r.get('status')!='Verified' for r in registry)}

def bibtex(registry:list[dict[str,Any]]) -> str:
    out=[]
    for r in registry:
        key=re.sub(r'[^A-Za-z0-9]+','',str(r.get('authors','ref')).split(',')[0]) or 'ref'
        key += str(r.get('year',''))
        fields=[]
        for name,val in [('title',r.get('title')),('author',r.get('authors')),('journal',r.get('journal')),('year',r.get('year')),('doi',r.get('doi'))]:
            if val: fields.append(f'  {name} = {{{val}}}')
        out.append('@article{'+key+',\n'+',\n'.join(fields)+'\n}')
    return '\n\n'.join(out)
