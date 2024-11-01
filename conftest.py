import os
import sys
import pytest
import logging
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent

# 将项目根目录添加到 Python 路径
sys.path.insert(0, str(ROOT_DIR))

def setup_logging():
    """配置日志级别"""
    # 设置第三方库的日志级别
    logging.getLogger('faker').setLevel(logging.INFO)  # 将Faker的日志级别设置为INFO
    logging.getLogger('asyncio').setLevel(logging.INFO)  # 设置asyncio的日志级别
    logging.getLogger('aiohttp').setLevel(logging.INFO)  # 设置aiohttp的日志级别
    
    # 设置根日志记录器
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# 在pytest会话开始时配置日志
def pytest_configure(config):
    setup_logging()
    
    # 添加标记说明
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers",
        "mysql: marks tests that require MySQL"
    )
    config.addinivalue_line(
        "markers",
        "mongodb: marks tests that require MongoDB"
    )

# 配置异步测试
def pytest_addoption(parser):
    parser.addini(
        'asyncio_mode',
        help='default mode for asyncio fixtures',
        default='auto'
    )
    parser.addini(
        'asyncio_fixture_loop_scope',
        help='default event loop scope for async fixtures',
        default='function'
    )

# 创建测试会话范围的事件循环
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# 配置测试环境
@pytest.fixture(autouse=True)
def setup_test_env():
    # 设置默认环境变量
    os.environ.setdefault("TEST_ENV", "test")
    os.environ.setdefault("TEST_REGION", "cn")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    
    yield