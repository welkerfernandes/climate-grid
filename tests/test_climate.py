import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.infrastructure import PublicAPI

@pytest.fixture
def client(tmp_path):
    provider=PublicAPI(client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(500))))
    with TestClient(create_app(str(tmp_path/'test.db'),provider)) as client:
        client.headers['X-API-Key']='local-alpha'
        yield client
    provider.close()

def test_auth_and_openapi(client):
    assert client.get('/').status_code==200
    assert client.get('/openapi.json').status_code==200
    assert client.get('/health').json()=={'status':'ok'}
    client.headers['X-API-Key']='invalid'
    assert client.get('/api/history').status_code==401
    assert client.post('/api/analyze',json={'mode':'demo'}).status_code==401

def test_tenant_history_delete(client):
    response=client.post('/api/analyze',json={'mode':'demo'})
    assert response.status_code==200, response.text
    ident=response.json()['snapshot_id']
    assert len(client.get('/api/history').json())==1
    client.headers['X-API-Key']='local-beta'
    assert client.get('/api/history').json()==[]
    assert client.delete('/api/history/'+ident).status_code==404
    client.headers['X-API-Key']='local-alpha'
    assert client.delete('/api/history/'+ident).json()=={'deleted':True}
    assert client.get('/api/history').json()==[]

def test_provider_failure_no_fake_fallback(client):
    result=client.post('/api/analyze',json={'mode':'live'})
    assert result.status_code==502
    assert client.get('/api/history').json()==[]

def test_demo_and_thresholds(client):
    result=client.post('/api/analyze',json={'mode':'demo'}).json()
    assert result['provenance']['mode']=='demo'
    assert len(result['days'])==7 and result['overall']=='high'
    assert result['days'][2]['reasons']==['heat','rain','wind']

def test_unknown_is_not_all_clear():
    from app.domain import Daily,assess
    daily=Daily(time=['2030-01-01'],temperature_2m_max=[None],precipitation_sum=[0],wind_speed_10m_max=[1])
    assert assess(daily,35,25,45)['overall']=='unknown'

def test_live_schema_and_provenance(tmp_path):
    def handler(request):
        assert request.url.params['wind_speed_unit']=='kmh'
        return httpx.Response(200,json={'daily':{'time':['2030-01-01'],'temperature_2m_max':[25],
                    'precipitation_sum':[0],'wind_speed_10m_max':[10]}})
    api=PublicAPI(httpx.Client(transport=httpx.MockTransport(handler)))
    with TestClient(create_app(str(tmp_path/'live.db'),api)) as c:
        response=c.post('/api/analyze',json={'mode':'live'},headers={'X-API-Key':'local-alpha'})
    assert response.status_code==200
    assert response.json()['provenance']['mode']=='live'
    assert response.json()['overall']=='normal'
    api.close()

def test_misaligned_series_rejected():
    from app.domain import Daily
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Daily(time=['2030-01-01'],temperature_2m_max=[],precipitation_sum=[0],wind_speed_10m_max=[1])

@pytest.mark.parametrize('fields',[{'latitude':91},{'longitude':-181},{'rain_mm':0}])
def test_invalid_configuration(client,fields):
    assert client.post('/api/analyze',json={'mode':'demo',**fields}).status_code==422
