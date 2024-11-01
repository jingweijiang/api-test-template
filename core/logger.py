import logging
import structlog
import uuid
import os
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

class Logger:
    def __init__(self):
        self._logger = self._setup_logger()
        self.case_id = None
        self.log_file = None

    def _setup_logger(self):
        """设置日志配置"""
        # 创建logs目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 配置基础日志
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] [%(case_id)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 配置structlog
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.render_to_log_kwargs,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger()

    def start_test_case(self, test_name: str):
        """开始新的测试用例，生成唯一case_id和日志文件"""
        self.case_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        log_filename = f"{self.case_id}_{test_name}.log"
        self.log_file = Path("logs") / log_filename

        # 配置文件处理器
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(case_id)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        # 获取根日志记录器并添加文件处理器
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.DEBUG)

        # 记录测试开始
        self.info(f"开始测试: {test_name}")
        self._write_separator("test start")

    def end_test_case(self):
        """结束测试用例的日志记录"""
        if self.log_file and self.log_file.exists():
            self._write_separator("test end")
            # 关闭并移除文件处理器
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                if isinstance(handler, logging.FileHandler) and handler.baseFilename == str(self.log_file):
                    handler.close()
                    root_logger.removeHandler(handler)

    def _write_separator(self, title: str):
        """写入分隔符"""
        separator = "=" * 50
        message = f"\n{separator} {title} {separator}"
        print(message)  # 控制台输出
        logging.debug(message)  # 文件输出

    def _format_dict(self, data: Dict) -> str:
        """格式化字典数据"""
        try:
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            return str(data)

    def _log_with_format(self, level: str, message: str, **kwargs: Any) -> None:
        """统一的日志记录格式"""
        formatted_message = f"{message}"
        if kwargs:
            formatted_data = "\n".join(f"{k}: {self._format_dict(v)}" for k, v in kwargs.items())
            formatted_message = f"{message}\n{formatted_data}"
        
        # 同时输出到控制台和文件
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {formatted_message}")
        getattr(logging, level.lower())(formatted_message, extra={"case_id": self.case_id})

    def info(self, message: str, **kwargs: Any) -> None:
        self._log_with_format("INFO", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log_with_format("ERROR", message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log_with_format("DEBUG", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log_with_format("WARNING", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log_with_format("CRITICAL", message, **kwargs)

    def log_request(
        self,
        method: str,
        url: str,
        headers: Dict = None,
        params: Dict = None,
        data: Dict = None,
    ) -> None:
        self._write_separator("request data")
        self.debug(
            "API Request Details",
            method=method,
            url=url,
            headers=headers or {},
            params=params or {},
            data=data or {}
        )

    def log_response(
        self,
        status_code: int,
        response_data: Any,
        timing: Dict[str, float] = None,
    ) -> None:
        """记录响应信息和性能分析"""
        self._write_separator("response data")
        
        # 记录基本响应信息
        self.debug(
            "API Response Details",
            status_code=status_code,
            response=response_data
        )
        
        # 记录性能分析
        if timing:
            self._write_separator("performance analysis")
            self.debug(
                "Request Timing Breakdown",
                **{
                    "DNS Resolution": f"{timing['dns_resolution']}ms",
                    "TCP Connection": f"{timing['tcp_connection']}ms",
                    "SSL/TLS Handshake": f"{timing['ssl_handshake']}ms",
                    "Request Send": f"{timing['request_send']}ms",
                    "Response Receive": f"{timing['response_receive']}ms",
                    "Total Time": f"{timing['total_time']}ms"
                }
            )
            
            # 性能警告
            self._analyze_performance(timing)

    def _analyze_performance(self, timing: Dict[str, float]) -> None:
        """分析性能并给出警告"""
        # DNS解析时间超过100ms警告
        if timing['dns_resolution'] > 100:
            self.warning(f"DNS resolution time ({timing['dns_resolution']}ms) is high")
        
        # TCP连接时间超过200ms警告
        if timing['tcp_connection'] > 200:
            self.warning(f"TCP connection time ({timing['tcp_connection']}ms) is high")
        
        # SSL握手时间超过300ms警告
        if timing['ssl_handshake'] > 300:
            self.warning(f"SSL handshake time ({timing['ssl_handshake']}ms) is high")
        
        # 总响应时间超过1000ms警告
        if timing['total_time'] > 1000:
            self.warning(f"Total request time ({timing['total_time']}ms) exceeds 1 second")

# 创建全局logger实例
logger = Logger() 