# -*- coding: utf-8 -*-


def test_read_main(client):
    response = client.get("/welcome/")
    assert response.status_code == 200

def test_join(client):
    response = client.post(
        "/welcome/join",
        json={"user_name": "test_user_name", "password": "123456"},
    )
    assert response.status_code == 200

def test_login(client):
    response = client.post(
        "/welcome/login",
        json={"user_name": "test_user_name", "password": "123456"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data.get('userinfo').get('display_name') == "test_user_name"

def test_change_user_name(client):
    response = client.post(
        "/settings/userinfo",
        headers={"x-consumer-id": "1"},
        json={"display_name": "changed_user_name"},
    )
    assert response.status_code == 200

def test_get_userinfo(client):
    response = client.get(
        "/settings/userinfo",
        headers={"x-consumer-id": "1"}
    )
    data = response.json()
    assert data.get('display_name') == 'changed_user_name'

def test_whoami(client):
    response = client.get(
        "/whoami",
        headers={"x-consumer-id": "1"}
    )
    data = response.json()
    assert data.get('userinfo').get('display_name') == 'changed_user_name'

