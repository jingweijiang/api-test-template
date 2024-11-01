import pytest
from typing import Optional
from clients.http_client import HTTPClient
from config.settings import settings
from core.logger import logger
from utils.db_handler import MySQLHandler, MongoHandler

class BaseTest:
    @pytest.fixture(autouse=True)
    def setup_test(self, request):
        """测试设置，自动管理日志"""
        # 设置日志
        test_name = f"{request.module.__name__}.{request.function.__name__}"
        logger.start_test_case(test_name)
        
        # 设置客户端
        self.http_client = HTTPClient(settings.base_url)
        self.logger = logger
        # self.mysql = MySQLHandler()
        # self.mongo = MongoHandler()
        
        yield
        
        # 测试清理代码
        logger.end_test_case()

    def verify_response(self, response, expected_status: int = 200):
        """验证响应结果"""
        actual_status = response.status
        assert actual_status == expected_status, \
            f"Expected status code {expected_status}, got {actual_status}"
        
    @staticmethod
    def get_test_data(file_path: str) -> dict:
        """获取测试数据"""
        # 实现测试数据读取逻辑
        pass