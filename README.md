# Enterprise API Testing Framework

一个企业级接口自动化测试框架，支持多环境、多协议、多数据源的自动化测试需求。

## 特性

- 支持多种协议：HTTP(S)、WebSocket、gRPC
- 多环境配置管理：测试环境、生产环境，支持多地区部署
- 数据库集成：MySQL、MongoDB、Redis支持
- 完整的测试报告：集成Allure报告系统
- 异步支持：基于aiohttp的异步HTTP客户端
- 分布式执行：支持多进程并行测试
- 数据驱动：支持多种数据源和参数化测试
- 环境隔离：支持Docker容器化运行

## 项目结构 
```
automation_framework/
├── conftest.py # pytest配置文件
├── pytest.ini # pytest全局配置
├── requirements.txt # 项目依赖
├── config/ # 配置管理
│ ├── environments/
│ │ ├── cn/ # 中国区配置
│ │ │ ├── test.yaml
│ │ │ └── prod.yaml
│ │ └── us/ # 美国区配置
│ │ ├── test.yaml
│ │ └── prod.yaml
├── core/ # 核心功能
├── utils/ # 工具类
├── clients/ # 客户端
└── tests/ # 测试用例
```

## 快速开始

### 环境要求

- Python 3.9+
- pip 或 poetry

### 安装

1. 克隆项目
```bash
git clone https://github.com/your-repo/automation_framework.git
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

### 配置
1. 环境变量设置
```bash
export ENVIRONMENT=cn
export REGION=test
```

2. 配置文件
config/environments/cn/test.yaml

```yaml
api:
  base_url: "http://api.test.cn.example.com"
  timeout: 30
  retry_times: 3

database:
  mysql:
    host: "mysql.test.cn.example.com"
    port: 3306
    user: "test_user"
    password: "test_password"
    database: "test_db"
    pool_size: 5
    
  mongodb:
    host: "mongodb.test.cn.example.com"
    port: 27017
    database: "test_db"
    username: "test_user"
    password: "test_password"
    max_pool_size: 100

redis:
  host: "redis.test.cn.example.com"
  port: 6379
  db: 0
  password: "test_redis_password"

test_accounts:
  admin:
    username: "admin_test"
    password: "admin_password"
  normal:
    username: "user_test"
    password: "user_password" 

```


### 运行测试

1. 运行所有测试
```bash
pytest tests/
```

2. 运行特定测试
```bash
# 运行特定测试文件
pytest tests/api/test_example.py

# 运行特定测试用例
pytest tests/api/test_example.py::TestExample::test_specific_case

# 运行标记的测试
pytest -m "mysql"  # 运行MySQL相关测试
pytest -m "mongodb"  # 运行MongoDB相关测试
pytest -m "integration"  # 运行集成测试
```

3. 并行执行测试
```bash
pytest -n auto  # 自动检测CPU核心数
pytest -n 4     # 指定4个进程并行执行
```

4. 生成测试报告
```bash
# 生成Allure报告
pytest --alluredir=./allure-results
allure serve allure-results

# 生成HTML报告
pytest --html=report.html
```

## 测试用例编写指南

### 基础测试用例
```python
from core.base_test import BaseTest

class TestExample(BaseTest):
    async def test_simple_get(self):
        """简单的GET请求测试"""
        response = await self.http_client.request(
            method="GET",
            endpoint="/api/example"
        )
        self.verify_response(response)
```

### 参数化测试
```python
import pytest

class TestParameterized(BaseTest):
    @pytest.mark.parametrize("test_input,expected", [
        ({"key": "value1"}, 200),
        ({"key": "value2"}, 201),
    ])
    async def test_with_parameters(self, test_input, expected):
        response = await self.http_client.request(
            method="POST",
            endpoint="/api/example",
            json=test_input
        )
        self.verify_response(response, expected)
```

### 数据库测试
```python
class TestDatabase(BaseTest):
    @pytest.mark.mysql
    def test_mysql_operations(self):
        """MySQL数据库操作测试"""
        result = self.mysql.execute_query(
            "SELECT * FROM users WHERE id = %s",
            (1,)
        )
        assert result is not None

    @pytest.mark.mongodb
    def test_mongodb_operations(self):
        """MongoDB数据库操作测试"""
        result = self.mongo.find(
            "users",
            {"username": "test_user"}
        )
        assert len(result) > 0
```

### 环境特定测试
```python
from utils.env_manager import test_env, prod_env

class TestEnvironments(BaseTest):
    @test_env
    def test_in_test_environment(self):
        """测试环境特定的测试"""
        assert "test" in self.http_client.base_url

    @prod_env
    def test_in_prod_environment(self):
        """生产环境特定的测试"""
        assert "prod" in self.http_client.base_url
```

## 开发指南

### 代码规范

- 使用black进行代码格式化
- 使用flake8进行代码检查
- 使用mypy进行类型检查

```bash
# 格式化代码
black .

# 代码检查
flake8 .

# 类型检查
mypy .

# 运行所有检查
make lint
```

### 提交规范

提交信息格式：
```
<type>(<scope>): <subject>

<body>

<footer>
```

## 项目配置

### 环境变量

| 变量名 | 说明 | 默认值 | 可选值 |
|--------|------|--------|--------|
| TEST_ENV | 测试环境 | test | test, prod |
| TEST_REGION | 地区 | cn | cn, us |
| LOG_LEVEL | 日志级别 | INFO | DEBUG, INFO, WARNING, ERROR |
| PYTEST_ADDOPTS | pytest额外参数 | - | -v, -s, etc. |

### 配置文件结构

```yaml
api:
  base_url: "http://api.example.com"
  timeout: 30
  retry_times: 3

database:
  mysql:
    host: "localhost"
    port: 3306
    # ...

  mongodb:
    host: "localhost"
    port: 27017
    # ...

redis:
  host: "localhost"
  port: 6379
  # ...

test_accounts:
  admin:
    username: "admin"
    password: "password"
  # ...
```

## 常见问题

1. 环境配置问题
   - 确保正确设置环境变量
   - 检查配置文件格式
   - 验证数据库连接信息

2. 依赖安装问题
   - 尝试使用 `pip install -r requirements.txt --no-cache-dir`
   - 检查Python版本兼容性
   - 确保系统安装了必要的开发库

3. 测试执行问题
   - 检查测试标记是否正确
   - 确认异步测试的正确配置
   - 验证数据库连接状态

4. 报告生成问题
   - 确保安装了allure命令行工具
   - 检查报告目录权限
   - 验证测试执行权限

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者：Your Name
- 邮箱：your.email@example.com
- 项目链接：https://github.com/your-username/automation-framework

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [pytest](https://docs.pytest.org/)
- [Allure Framework](https://docs.qameta.io/allure/)
