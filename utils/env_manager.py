import os
from functools import wraps
from typing import Callable
import pytest
from config.settings import Settings

class EnvironmentManager:
    @staticmethod
    def set_env(env: str, region: str):
        """设置测试环境和地区"""
        os.environ["TEST_ENV"] = env
        os.environ["TEST_REGION"] = region
        # 重新加载配置
        return Settings()

    @staticmethod
    def env_decorator(env: str, region: str):
        """环境装饰器，用于特定环境的测试"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                original_env = os.getenv("TEST_ENV")
                original_region = os.getenv("TEST_REGION")
                
                try:
                    EnvironmentManager.set_env(env, region)
                    return func(*args, **kwargs)
                finally:
                    # 恢复原始环境设置
                    EnvironmentManager.set_env(original_env, original_region)
            return wrapper
        return decorator

# 创建便捷的装饰器
test_env = EnvironmentManager.env_decorator("test", "cn")
prod_env = EnvironmentManager.env_decorator("prod", "cn")
global_test = EnvironmentManager.env_decorator("test", "global") 