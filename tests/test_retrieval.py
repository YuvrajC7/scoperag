import pytest
from fastapi.testclient import TestClient
from app import app
from core import KnowledgeStore,seed

@pytest.fixture
def store():
    s=KnowledgeStore();seed(s,12);yield s;s.close()

@pytest.mark.parametrize('tenant',['acme','beacon'])
@pytest.mark.parametrize('mode',['lexical','character','hybrid'])
def test_authorized_only(store,tenant,mode):
    r=store.answer(tenant,'reader','product1 retention',mode)
    assert r['hits'] and all(h['id'].startswith(tenant) for h in r['hits'])
    assert all(not h['id'].endswith('-0') for h in r['hits'])
    assert r['citations_valid']

def test_revocation_invalidates_cache(store):
    assert not store.answer('acme','reader','product1 retention')['cache_hit']
    assert store.answer('acme','reader','product1 retention')['cache_hit']
    store.put('acme-1','acme','retention product1','revoked private content',['manager'])
    r=store.answer('acme','reader','product1 retention')
    assert not r['cache_hit'] and all(h['id']!='acme-1' for h in r['hits'])

def test_unknown_principal_abstains(store):
    assert store.answer('acme','outsider','product1')['engine']=='abstain'

def test_version_changes(store):
    store.put('acme-1','acme','product1 retention','new version',['reader'])
    assert store.retrieve('acme','reader','product1')['hits'][0]['version']==2

def test_tenant_cannot_move(store):
    with pytest.raises(ValueError):store.put('acme-1','beacon','x','x',['reader'])

def test_api_identity_not_body():
    c=TestClient(app)
    assert c.post('/query',json={'query':'x'}).status_code==401
    r=c.post('/query',headers={'Authorization':'Bearer demo-acme-reader'},json={'query':'product1','tenant':'beacon'}).json()
    assert all(h['id'].startswith('acme') for h in r['hits'])
