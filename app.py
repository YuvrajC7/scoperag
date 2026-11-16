import os
from fastapi import FastAPI,Header,HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel,Field
from core import KnowledgeStore,seed
from ui import page

app=FastAPI(title='ScopeRAG',version='0.1.0')
store=KnowledgeStore(os.getenv('SCOPERAG_DB',':memory:'));seed(store)
# Public synthetic demo identities only. Do not expose this authentication scheme publicly.
TOKENS={'demo-acme-reader':('acme','reader'),'demo-beacon-reader':('beacon','reader')}
class Query(BaseModel):
    query:str=Field(min_length=1,max_length=500)
    mode:str='hybrid'
class Demo(BaseModel):
    query:str='product1 retention window'

@app.get('/',response_class=HTMLResponse)
def home():return page('ScopeRAG','Inspect authorized evidence, exact version citations, cache invalidation, and retrieval baselines. Offline answers are extractive.',{'query':'product1 retention window'})

@app.post('/query')
def query(q:Query,authorization:str=Header(default='')):
    identity=TOKENS.get(authorization.removeprefix('Bearer '))
    if not identity:raise HTTPException(401,'Use a documented synthetic demo token')
    try:return store.answer(*identity,q.query,q.mode)
    except ValueError as e:raise HTTPException(400,str(e))

@app.post('/demo')
def demo(q:Demo):
    local=KnowledgeStore();seed(local)
    try:
        first=local.answer('acme','reader',q.query)
        cached=local.answer('acme','reader',q.query)
        if first['hits']:
            h=first['hits'][0]
            local.put(h['id'],'acme',h['title'],h['text'],['manager'])
        after=local.answer('acme','reader',q.query)
        return {'before':first,'cached':cached,'after_revocation':after}
    finally:local.close()
