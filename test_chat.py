from fastapi.testclient import TestClient

from app import app
from conversation_manager import is_recommendable

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_chat_initial_followup_missing_info():
    response = client.post(
        '/chat',
        json={
            'messages': [
                {
                    'role': 'user',
                    'content': 'I need an assessment',
                }
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['recommendations'] == []
    assert 'what role are you hiring for' in data['reply'].lower()
    assert data['end_of_conversation'] is False


def test_chat_recommendations_for_senior_personality_situational():
    response = client.post(
        '/chat',
        json={
            'messages': [
                {
                    'role': 'user',
                    'content': 'I need a personality and situational judgment assessment for a senior operations manager',
                }
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['reply'].startswith('Got it. Here are')
    assert isinstance(data['recommendations'], list)
    assert len(data['recommendations']) > 0
    assert all(
        isinstance(item, dict)
        and 'name' in item
        and 'url' in item
        and 'test_type' in item
        for item in data['recommendations']
    )
    assert data['end_of_conversation'] is False


def test_chat_example_conversation_from_prompt():
    response = client.post(
        '/chat',
        json={
            'messages': [
                {'role': 'user', 'content': 'Hiring a Java developer who works with stakeholders'},
                {'role': 'assistant', 'content': 'Sure. What is seniority level?'},
                {'role': 'user', 'content': 'Mid-level, around 4 years'},
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['reply'].startswith('Got it. Here are')
    assert 1 <= len(data['recommendations']) <= 10
    assert all(
        isinstance(item, dict)
        and 'name' in item
        and 'url' in item
        and 'test_type' in item
        for item in data['recommendations']
    )
    assert data['end_of_conversation'] is False


def test_chat_refinement_updates_shortlist():
    response = client.post(
        '/chat',
        json={
            'messages': [
                {
                    'role': 'user',
                    'content': 'Hiring a mid-level Java developer who works with stakeholders',
                },
                {
                    'role': 'assistant',
                    'content': 'Sure. What is seniority level?',
                },
                {
                    'role': 'user',
                    'content': 'Actually, add personality tests.',
                },
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['reply'].startswith('Got it. Here are')
    assert isinstance(data['recommendations'], list)
    assert 1 <= len(data['recommendations']) <= 10
    assert data['end_of_conversation'] is False


def test_chat_comparison_request():
    response = client.post(
        '/chat',
        json={
            'messages': [
                {'role': 'user', 'content': 'Compare OPQ and GSA'}
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert 'opq' in data['reply'].lower() or 'gsa' in data['reply'].lower()
    assert data['recommendations'] == []
    assert data['end_of_conversation'] is False


def test_chat_refusal_response():
    response = client.post(
        '/chat',
        json={
            'messages': [
                {
                    'role': 'user',
                    'content': 'Is it legal to recommend an assessment for compensation decisions?',
                }
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert 'legal' in data['reply'].lower()
    assert data['recommendations'] == []
    assert data['end_of_conversation'] is False


def test_root_route():
    response = client.get('/')
    assert response.status_code == 200
    assert 'Use GET /health and POST /chat' in response.json().get('message', '')


def test_invalid_json_returns_helpful_message():
    response = client.post(
        '/chat',
        data=b'{"messages":[{"role":"user","content":"Hi"}',
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 422
    assert isinstance(response.json(), dict)
    assert 'Invalid JSON body' in response.json().get('detail', '')


def test_excludes_non_test_catalog_items():
    assert not is_recommendable({'name': 'Global Skills Development Report'})
    assert not is_recommendable({'name': 'Sales Interview Guide'})
    assert not is_recommendable({'name': 'OPQ Leadership Report'})
    assert is_recommendable({'name': '.NET Framework 4.5'})


def test_recommendations_do_not_include_reports_or_guides():
    response = client.post(
        '/chat',
        json={
            'messages': [
                {'role': 'user', 'content': 'Hiring a mid-level sales manager for a commercial role.'},
                {'role': 'assistant', 'content': 'Sure. What seniority level is this?'},
                {'role': 'user', 'content': 'Mid-level'}
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['recommendations'], 'Expected at least one recommendation'
    for item in data['recommendations']:
        name = item['name'].lower()
        assert 'report' not in name
        assert 'guide' not in name
        assert 'profile' not in name
        assert 'solution' not in name
        assert 'pack' not in name
