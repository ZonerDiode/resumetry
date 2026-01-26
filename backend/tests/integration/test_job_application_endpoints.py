"""Tests for job application API endpoints via TestClient."""
from datetime import date


BASE_URL = '/api/v1/applications'


class TestCreateEndpoint:

    def test_create_minimal(self, client, sample_application_data):
        response = client.post(BASE_URL, json=sample_application_data)
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert data['company'] == 'Acme Corp'
        assert data['role'] == 'Software Engineer'
        assert data['interestLevel'] == 2

    def test_create_full(self, client, full_application_data):
        response = client.post(BASE_URL, json=full_application_data)
        assert response.status_code == 201
        data = response.json()
        assert data['salary'] == '$150k'
        assert data['status'] == 'interview'
        assert len(data['notes']) == 1

    def test_create_returns_camel_case(self, client, sample_application_data):
        response = client.post(BASE_URL, json=sample_application_data)
        data = response.json()
        assert 'interestLevel' in data
        assert 'appliedDate' in data
        assert 'statusDate' in data
        assert 'interest_level' not in data
        assert 'applied_date' not in data

    def test_create_missing_required_field(self, client):
        response = client.post(BASE_URL, json={'company': 'Acme'})
        assert response.status_code == 422

    def test_create_invalid_interest_level(self, client):
        response = client.post(BASE_URL, json={
            'company': 'Acme', 'role': 'Dev', 'interestLevel': 5,
        })
        assert response.status_code == 422

    def test_create_invalid_status(self, client):
        response = client.post(BASE_URL, json={
            'company': 'Acme', 'role': 'Dev', 'interestLevel': 2,
            'status': 'invalid_status',
        })
        assert response.status_code == 422

    def test_create_empty_company(self, client):
        response = client.post(BASE_URL, json={
            'company': '', 'role': 'Dev', 'interestLevel': 2,
        })
        assert response.status_code == 422

    def test_create_with_notes(self, client):
        response = client.post(BASE_URL, json={
            'company': 'Acme', 'role': 'Dev', 'interestLevel': 2,
            'notes': [
                {'occurDate': str(date.today()), 'description': 'Applied online'},
            ],
        })
        assert response.status_code == 201
        assert len(response.json()['notes']) == 1


class TestListEndpoint:

    def test_list_empty(self, client):
        response = client.get(BASE_URL)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_after_creates(self, client, sample_application_data):
        client.post(BASE_URL, json=sample_application_data)
        client.post(BASE_URL, json={
            'company': 'Other Corp', 'role': 'Manager', 'interestLevel': 1,
        })
        response = client.get(BASE_URL)
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_response_structure(self, client, created_application):
        response = client.get(BASE_URL)
        data = response.json()
        assert len(data) == 1
        item = data[0]
        assert 'id' in item
        assert 'company' in item
        assert 'role' in item
        assert 'interestLevel' in item


class TestGetByIdEndpoint:

    def test_get_existing(self, client, created_application):
        app_id = created_application['id']
        response = client.get(f'{BASE_URL}/{app_id}')
        assert response.status_code == 200
        assert response.json()['id'] == app_id

    def test_get_nonexistent(self, client):
        response = client.get(f'{BASE_URL}/nonexistent-id')
        assert response.status_code == 404

    def test_404_detail_message(self, client):
        response = client.get(f'{BASE_URL}/fake-id')
        assert 'fake-id' in response.json()['detail']


class TestUpdateEndpoint:

    def test_patch_single_field(self, client, created_application):
        app_id = created_application['id']
        response = client.patch(
            f'{BASE_URL}/{app_id}',
            json={'company': 'Updated Corp'},
        )
        assert response.status_code == 200
        assert response.json()['company'] == 'Updated Corp'
        assert response.json()['role'] == created_application['role']

    def test_patch_status(self, client, created_application):
        app_id = created_application['id']
        response = client.patch(
            f'{BASE_URL}/{app_id}',
            json={'status': 'interview'},
        )
        assert response.status_code == 200
        assert response.json()['status'] == 'interview'

    def test_patch_nonexistent(self, client):
        response = client.patch(
            f'{BASE_URL}/nonexistent-id',
            json={'company': 'NewCo'},
        )
        assert response.status_code == 404

    def test_patch_empty_body(self, client, created_application):
        app_id = created_application['id']
        response = client.patch(f'{BASE_URL}/{app_id}', json={})
        assert response.status_code == 200
        assert response.json()['company'] == created_application['company']

    def test_patch_invalid_field_value(self, client, created_application):
        app_id = created_application['id']
        response = client.patch(
            f'{BASE_URL}/{app_id}',
            json={'interestLevel': 10},
        )
        assert response.status_code == 422

    def test_patch_notes(self, client, created_application):
        app_id = created_application['id']
        response = client.patch(
            f'{BASE_URL}/{app_id}',
            json={
                'notes': [
                    {'occurDate': str(date.today()), 'description': 'Updated note'},
                ],
            },
        )
        assert response.status_code == 200
        assert len(response.json()['notes']) == 1


class TestDeleteEndpoint:

    def test_delete_existing(self, client, created_application):
        app_id = created_application['id']
        response = client.delete(f'{BASE_URL}/{app_id}')
        assert response.status_code == 204

    def test_delete_nonexistent(self, client):
        response = client.delete(f'{BASE_URL}/nonexistent-id')
        assert response.status_code == 404

    def test_delete_then_get_returns_404(self, client, created_application):
        app_id = created_application['id']
        client.delete(f'{BASE_URL}/{app_id}')
        response = client.get(f'{BASE_URL}/{app_id}')
        assert response.status_code == 404

    def test_delete_idempotent_second_call_404(self, client, created_application):
        app_id = created_application['id']
        client.delete(f'{BASE_URL}/{app_id}')
        response = client.delete(f'{BASE_URL}/{app_id}')
        assert response.status_code == 404

    def test_delete_does_not_affect_others(self, client, sample_application_data):
        resp1 = client.post(BASE_URL, json=sample_application_data)
        resp2 = client.post(BASE_URL, json={
            'company': 'Other', 'role': 'PM', 'interestLevel': 1,
        })
        client.delete(f'{BASE_URL}/{resp1.json()["id"]}')
        remaining = client.get(BASE_URL).json()
        assert len(remaining) == 1
        assert remaining[0]['id'] == resp2.json()['id']
