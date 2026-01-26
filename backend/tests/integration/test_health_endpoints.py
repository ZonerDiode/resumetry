"""Tests for health and ping endpoints."""


class TestHealthEndpoint:

    def test_health_returns_200(self, client):
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_response_body(self, client):
        data = client.get('/health').json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'resumetry-api'


class TestPingEndpoint:

    def test_ping_returns_200(self, client):
        response = client.get('/api/v1/ping')
        assert response.status_code == 200

    def test_ping_response_body(self, client):
        data = client.get('/api/v1/ping').json()
        assert data['message'] == 'pong'
        assert data['version'] == '1.0.0'
