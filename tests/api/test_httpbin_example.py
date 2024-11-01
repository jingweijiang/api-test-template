import pytest
import json
from core.base_test import BaseTest
from datetime import datetime
from typing import Dict

class TestHttpBinAPI(BaseTest):
    def setup_method(self):
        """测试方法级别的设置"""
        self.base_url = "https://httpbin.org"
        self.test_data = {
            "name": f"test_user_{datetime.now().timestamp()}",
            "age": 25,
            "email": f"test_{datetime.now().timestamp()}@example.com"
        }

    @pytest.mark.parametrize("status_code", [200, 201, 404, 500])
    async def test_status_code(self, status_code):
        """测试不同状态码的响应"""
        response = await self.http_client.request(
            method="GET",
            endpoint=f"/status/{status_code}"
        )
        assert response.status == status_code

    @pytest.mark.parametrize("test_input,expected", [
        ({"name": "test", "age": 20}, 200),
        ({"name": "test"}, 200),
        ({"age": 20}, 200),
        ({}, 200)
    ])
    async def test_get_with_params(self, test_input: Dict, expected: int):
        """测试GET请求参数验证"""
        response = await self.http_client.request(
            method="GET",
            endpoint="/get",
            params=test_input
        )
        self.verify_response(response, expected)
        # 使用response.data访问解析后的数据
        assert response.data["args"] == test_input

    @pytest.mark.parametrize("content_type", [
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data"
    ])
    async def test_post_content_types(self, content_type):
        """测试不同Content-Type的POST请求"""
        headers = {"Content-Type": content_type}
        response = await self.http_client.request(
            method="POST",
            endpoint="/post",
            json=self.test_data,
            headers=headers
        )
        self.verify_response(response)
        assert response.data["headers"]["Content-Type"] == content_type

    async def test_complex_scenario(self):
        """测试复杂场景：参数依赖的接口流"""
        # 步骤1：POST创建数据
        post_response = await self.http_client.request(
            method="POST",
            endpoint="/post",
            json=self.test_data
        )
        self.verify_response(post_response)
        post_data = post_response.json()
        
        # 从POST响应中提取数据用于后续请求
        response_data = post_data["json"]
        user_name = response_data["name"]

        # 步骤2：使用前一个接口的响应数据进行GET请求
        get_response = await self.http_client.request(
            method="GET",
            endpoint="/get",
            params={"name": user_name}
        )
        self.verify_response(get_response)
        get_data = get_response.json()
        assert get_data["args"]["name"] == user_name

        # 步骤3：PUT更新数据
        updated_data = {**self.test_data, "age": 26}
        put_response = await self.http_client.request(
            method="PUT",
            endpoint="/put",
            json=updated_data
        )
        self.verify_response(put_response)
        assert put_response.json()["json"]["age"] == 26

    @pytest.mark.parametrize("delay", [1, 2])
    async def test_delayed_response(self, delay):
        """测试延迟响应"""
        response = await self.http_client.request(
            method="GET",
            endpoint=f"/delay/{delay}"
        )
        self.verify_response(response)

    async def test_headers_verification(self):
        """测试请求头验证"""
        custom_headers = {
            "X-Custom-Header": "test_value",
            "User-Agent": "PyTest/1.0"
        }
        response = await self.http_client.request(
            method="GET",
            endpoint="/headers",
            headers=custom_headers
        )
        self.verify_response(response)
        response_headers = response.json()["headers"]
        
        for key, value in custom_headers.items():
            assert response_headers[key] == value

    @pytest.mark.parametrize("test_input", [
        {"key1": "value1"},
        {"key1": "value1", "key2": "value2"},
        {"key1": ["value1", "value2"]},
        {"key1": {"nested_key": "nested_value"}}
    ])
    async def test_different_data_structures(self, test_input):
        """测试不同数据结构的请求"""
        response = await self.http_client.request(
            method="POST",
            endpoint="/post",
            json=test_input
        )
        self.verify_response(response)
        assert response.json()["json"] == test_input

    async def test_cookies_handling(self):
        """测试Cookie处理"""
        # 设置Cookie
        cookies = {"test_cookie": "test_value"}
        response = await self.http_client.request(
            method="GET",
            endpoint="/cookies/set",
            params=cookies
        )
        self.verify_response(response)

        # 验证Cookie
        cookie_response = await self.http_client.request(
            method="GET",
            endpoint="/cookies"
        )
        self.verify_response(cookie_response)
        assert cookie_response.json()["cookies"]["test_cookie"] == "test_value"

    @pytest.mark.parametrize("compression", ["gzip", "deflate"])
    async def test_compression(self, compression):
        """测试不同压缩方式"""
        headers = {"Accept-Encoding": compression}
        response = await self.http_client.request(
            method="GET",
            endpoint="/gzip" if compression == "gzip" else "/deflate",
            headers=headers
        )
        self.verify_response(response)
        assert response.headers.get("content-encoding") == compression 