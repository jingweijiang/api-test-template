import pytest
from core.base_test import BaseTest

class TestUserAPI(BaseTest):
    @pytest.mark.parametrize("user_data", [
        {"username": "test_user1", "email": "test1@example.com"},
        {"username": "test_user2", "email": "test2@example.com"}
    ])
    async def test_create_user(self, user_data):
        """测试创建用户接口"""
        response = await self.http_client.request(
            method="POST",
            endpoint="/users",
            json=user_data
        )
        
        self.verify_response(response, 201)
        response_data = response.json()
        assert response_data["username"] == user_data["username"]
        assert response_data["email"] == user_data["email"] 