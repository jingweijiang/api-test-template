import pytest
from core.base_test import BaseTest
from datetime import datetime
from utils.env_manager import test_env, prod_env, global_test

class TestUserDatabase(BaseTest):
    def setup_method(self):
        """测试方法级别的设置"""
        self.test_user = {
            "username": f"test_user_{datetime.now().timestamp()}",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @test_env
    def test_cn_test_environment(self):
        """测试中国测试环境"""
        assert "cn" in self.http_client.base_url
        assert "test" in self.http_client.base_url

    @global_test
    def test_global_environment(self):
        """测试全球环境"""
        assert "global" in self.http_client.base_url

    @pytest.mark.parametrize("region", ["cn", "global"])
    def test_multi_region(self, region):
        """测试多地区配置"""
        settings = EnvironmentManager.set_env("test", region)
        assert region in settings.base_url

    @test_env
    def test_database_connection(self):
        """测试数据库连接配置"""
        # 使用之前实现的数据库操作
        results = self.mysql.execute_query("SELECT 1")
        assert results is not None

    @pytest.mark.mysql
    def test_mysql_user_operations(self):
        """测试MySQL用户CRUD操作"""
        # 创建用户
        insert_query = """
            INSERT INTO users (username, email, created_at) 
            VALUES (%s, %s, %s)
        """
        self.mysql.execute_update(
            insert_query, 
            (self.test_user["username"], self.test_user["email"], self.test_user["created_at"])
        )

        # 查询用户
        select_query = "SELECT * FROM users WHERE username = %s"
        results = self.mysql.execute_query(select_query, (self.test_user["username"],))
        assert len(results) == 1
        assert results[0]["email"] == self.test_user["email"]

        # 更新用户
        new_email = "updated_" + self.test_user["email"]
        update_query = "UPDATE users SET email = %s WHERE username = %s"
        affected_rows = self.mysql.execute_update(
            update_query, 
            (new_email, self.test_user["username"])
        )
        assert affected_rows == 1

        # 删除用户
        delete_query = "DELETE FROM users WHERE username = %s"
        affected_rows = self.mysql.execute_update(delete_query, (self.test_user["username"],))
        assert affected_rows == 1

    @pytest.mark.mongodb
    def test_mongodb_user_operations(self):
        """测试MongoDB用户CRUD操作"""
        collection = "users"

        # 创建用户
        user_id = self.mongo.insert_one(collection, self.test_user)
        assert user_id is not None

        # 查询用户
        users = self.mongo.find(
            collection, 
            {"username": self.test_user["username"]}
        )
        assert len(users) == 1
        assert users[0]["email"] == self.test_user["email"]

        # 更新用户
        new_email = "updated_" + self.test_user["email"]
        modified_count = self.mongo.update_many(
            collection,
            {"username": self.test_user["username"]},
            {"email": new_email}
        )
        assert modified_count == 1

        # 删除用户
        deleted_count = self.mongo.delete_many(
            collection,
            {"username": self.test_user["username"]}
        )
        assert deleted_count == 1

    @pytest.mark.integration
    async def test_user_api_with_db_verification(self):
        """测试用户API与数据库集成验证"""
        # 通过API创建用户
        response = await self.http_client.request(
            method="POST",
            endpoint="/users",
            json=self.test_user
        )
        self.verify_response(response, 201)
        
        # 验证数据库中的数据
        users = self.mongo.find(
            "users",
            {"username": self.test_user["username"]}
        )
        assert len(users) == 1
        assert users[0]["email"] == self.test_user["email"] 