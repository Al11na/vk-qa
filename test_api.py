import os

import yaml
import pytest
import requests
from jsonschema import validate
from jsonschema.exceptions import ValidationError

BASE_URL = "https://jsonplaceholder.typicode.com"
REQUEST_TIMEOUT = 10


def load_openapi_schema():
    yaml_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "openapi.yaml")
    with open(yaml_path, "r", encoding="utf-8") as spec_file:
        return yaml.safe_load(spec_file)


OPENAPI_SPEC = load_openapi_schema()
NEW_POST_SCHEMA = OPENAPI_SPEC["components"]["schemas"]["NewPost"]
POST_SCHEMA = OPENAPI_SPEC["components"]["schemas"]["Post"]


def test_get_all_posts_success():
    """Получение списка постов возвращает непустой список объектов по контракту."""
    response = requests.get(f"{BASE_URL}/posts", timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200
    posts = response.json()
    assert isinstance(posts, list)
    assert posts
    for post in posts:
        validate(instance=post, schema=POST_SCHEMA)


def test_get_single_post_contract_validation():
    """Ответ реального API соответствует схеме Post из OpenAPI."""
    response = requests.get(f"{BASE_URL}/posts/1", timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    validate(instance=data, schema=POST_SCHEMA)
    assert data["id"] == 1


def test_create_post_success():
    """POST возвращает созданный по контракту пост (JSONPlaceholder не сохраняет его)."""
    payload = {
        "title": "VK QA Automation Course",
        "body": "Implementing REST API Contract tests",
        "userId": 42
    }
    response = requests.post(
        f"{BASE_URL}/posts", json=payload, timeout=REQUEST_TIMEOUT
    )
    assert response.status_code == 201
    data = response.json()
    validate(instance=data, schema=POST_SCHEMA)
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]
    assert data["userId"] == payload["userId"]
    assert isinstance(data["id"], int)


def test_get_post_by_boundary_id():
    """Запрос поста с наибольшим существующим ID в фикстурном наборе."""
    response = requests.get(f"{BASE_URL}/posts/100", timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200
    post = response.json()
    validate(instance=post, schema=POST_SCHEMA)
    assert post["id"] == 100


def test_create_post_empty_fields_are_accepted_by_mock():
    """Контракт требует поля, но mock API принимает пустые строки без валидации."""
    with pytest.raises(ValidationError):
        validate(instance={"body": "", "userId": 1}, schema=NEW_POST_SCHEMA)

    payload = {
        "title": "",
        "body": "",
        "userId": 1
    }
    response = requests.post(
        f"{BASE_URL}/posts", json=payload, timeout=REQUEST_TIMEOUT
    )
    assert response.status_code == 201
    data = response.json()
    validate(instance=data, schema=POST_SCHEMA)
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]


def test_get_post_out_of_bounds():
    """ID за пределами набора постов возвращает 404."""
    response = requests.get(f"{BASE_URL}/posts/101", timeout=REQUEST_TIMEOUT)
    assert response.status_code == 404


@pytest.mark.parametrize("invalid_id", ["invalid_string", "status/404", "-999"])
def test_get_post_invalid_id_format(invalid_id):
    """Несуществующий или некорректный ID ресурса возвращает 404."""
    response = requests.get(
        f"{BASE_URL}/posts/{invalid_id}", timeout=REQUEST_TIMEOUT
    )
    assert response.status_code == 404
