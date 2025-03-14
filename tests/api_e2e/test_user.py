from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_get_healthcheck():
    response = client.get("/api/v1/healthcheck/")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_create_and_get_user(test_client, user_particulier_payload):
    response = test_client.post("/api/v1/users/", json=user_particulier_payload)
    response_json = response.json()
    assert response.status_code == 201

    # Get the created user
    response = test_client.get(f"/api/v1/users/{response_json['id']}")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["email"] == user_particulier_payload["email"]
    assert response_json["nom"] == user_particulier_payload["nom"]
    assert response_json["prenom"] == user_particulier_payload["prenom"]
    assert response_json["role"] == user_particulier_payload["role"]
    assert response_json["telephone"] == user_particulier_payload["telephone"]
    
def test_already_used_email_error(test_client, user_particulier_payload):
    response = test_client.post("/api/v1/users/", json=user_particulier_payload)
    response_json = response.json()
    assert response.status_code == 201

    response = test_client.post("/api/v1/users/", json=user_particulier_payload)
    response_json = response.json()
    assert response.status_code == 400
    assert response_json["detail"] == "L'utilisateur avec cet email existe déjà dans le système."
    
# def test_get_token(test_client, user_particulier_payload):
#     response = test_client.post("/api/v1/users/", json=user_particulier_payload)
#     response_json = response.json()
#     assert response.status_code == 201
#
#     response = test_client.post("/api/v1/users/token", json='{ username:  {}, password: {}}'.format(user_particulier_payload["email"], user_particulier_payload["password"]))
#     response_json = response.json()
#     assert response.status_code == 200
