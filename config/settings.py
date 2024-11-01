import os
import yaml
from pathlib import Path
from typing import Dict, Any
import re

class Settings:
    def __init__(self):
        self.env = os.getenv("TEST_ENV", "test")
        self.region = os.getenv("TEST_REGION", "cn")
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件并处理环境变量"""
        config_path = Path(__file__).parent / "environments" / self.region / f"{self.env}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return self._process_env_vars(config)

    def _process_env_vars(self, config: Dict) -> Dict:
        """递归处理配置中的环境变量引用"""
        def _process_value(value):
            if isinstance(value, str):
                # 匹配 ${VAR_NAME} 格式的环境变量引用
                env_vars = re.findall(r'\${([^}]+)}', value)
                for env_var in env_vars:
                    env_value = os.getenv(env_var)
                    if env_value is None:
                        raise ValueError(f"Environment variable {env_var} not set")
                    value = value.replace(f"${{{env_var}}}", env_value)
                return value
            elif isinstance(value, dict):
                return {k: _process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_process_value(item) for item in value]
            return value

        return _process_value(config)

    @property
    def base_url(self) -> str:
        return self._config["api"]["base_url"]

    @property
    def api_config(self) -> Dict[str, Any]:
        return self._config["api"]

    @property
    def db_config(self) -> Dict[str, Any]:
        return self._config["database"]

    @property
    def redis_config(self) -> Dict[str, Any]:
        return self._config["redis"]

    @property
    def test_accounts(self) -> Dict[str, Any]:
        return self._config.get("test_accounts", {})

    def get_region_specific_config(self, key: str) -> Any:
        """获取特定地区的配置"""
        return self._config.get(key, {})

settings = Settings() 