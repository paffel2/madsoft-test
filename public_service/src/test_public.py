from main import app

import pytest
from fastapi.testclient import TestClient
import unittest
from unittest.mock import patch
from schemas import MemeDescription
from models import Meme
from exceptions import MemeDoesntExist, S3NotWorking


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


async def test_get_memes(client):
    async def mocked_get_memes(*args, **kwargs):
        return [MemeDescription(name="test_name", link="some_link")]

    with patch("router.Memes.get_memes", mocked_get_memes):
        response = client.get("/memes/")
        assert response.status_code == 200

        expected_json = {"memes": [{"name": "test_name", "link": "some_link"}]}

        assert response.json() == expected_json


async def test_get_meme_by_id(client):
    async def mocked_get_meme(*args, **kwargs):
        return Meme(name="test_name", id=1)

    async def mocked_get_image(*args, **kwargs):
        return ("", "image/jpg")

    with patch("router.Memes.get_meme_by_id", mocked_get_meme):
        with patch("router.get_image_from_s3", mocked_get_image):
            response = client.get("/memes/1")
            assert response.status_code == 200


async def test_add_meme(client):
    async def mocked_add_meme(*args, **kwargs):
        return 1

    async def mocked_add_image(*args, **kwargs):
        return None

    with patch("router.Memes.add_meme", mocked_add_meme):
        with patch("router.add_image_to_s3", mocked_add_image):
            response = client.post("/memes/?name=test_name", files={"image": ""})
            assert response.status_code == 201


async def test_update_meme(client):
    async def mocked_update_meme(*args, **kwargs):
        return None

    async def mocked_add_image(*args, **kwargs):
        return None

    with patch("router.Memes.update_meme", mocked_update_meme):
        with patch("router.add_image_to_s3", mocked_add_image):
            response = client.put("/memes/1?new_name=123")
            assert response.status_code == 201


async def test_delete_meme(client):
    async def mocked_delete_meme(*args, **kwargs):
        return None

    async def mocked_delete_image(*args, **kwargs):
        return None

    with patch("router.Memes.delete_meme", mocked_delete_meme):
        with patch("router.delete_image_from_s3", mocked_delete_image):
            response = client.delete("/memes/1")
            assert response.status_code == 200


async def test_meme_not_found(client):
    async def mocked_get_meme(*args, **kwargs):
        raise MemeDoesntExist

    with patch("router.Memes.get_meme_by_id", mocked_get_meme):
        response = client.get("/memes/1")
        assert response.status_code == 400
        expected_json = {"message": "error", "content": "meme doesn't exist"}
        assert response.json() == expected_json


async def test_s3_not_working(client):
    async def mocked_get_meme(*args, **kwargs):
        return Meme(name="test_name", id=1)

    async def mocked_get_image(*args, **kwargs):
        raise S3NotWorking

    with patch("router.Memes.get_meme_by_id", mocked_get_meme):
        with patch("router.get_image_from_s3", mocked_get_image):
            response = client.get("/memes/1")
            assert response.status_code == 400
            expected_json = {"message": "error", "content": "s3 doesn't working"}
            assert response.json() == expected_json
