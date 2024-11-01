import aiohttp
import asyncio
import time
import socket
import ssl
from typing import Dict, Any, Optional, Union, Tuple
from core.logger import logger
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RequestTiming:
    """请求各阶段耗时"""
    start_time: float = 0.0
    dns_start: float = 0.0
    dns_end: float = 0.0
    connect_start: float = 0.0
    connect_end: float = 0.0
    ssl_start: float = 0.0
    ssl_end: float = 0.0
    send_start: float = 0.0
    send_end: float = 0.0
    receive_start: float = 0.0
    receive_end: float = 0.0

    @property
    def dns_time(self) -> float:
        """DNS解析耗时"""
        return self.dns_end - self.dns_start if self.dns_end > 0 else 0

    @property
    def connect_time(self) -> float:
        """TCP连接耗时"""
        return self.connect_end - self.connect_start if self.connect_end > 0 else 0

    @property
    def ssl_time(self) -> float:
        """SSL/TLS握手耗时"""
        return self.ssl_end - self.ssl_start if self.ssl_end > 0 else 0

    @property
    def send_time(self) -> float:
        """请求发送耗时"""
        return self.send_end - self.send_start if self.send_end > 0 else 0

    @property
    def receive_time(self) -> float:
        """响应接收耗时"""
        return self.receive_end - self.receive_start if self.receive_end > 0 else 0

    @property
    def total_time(self) -> float:
        """总耗时"""
        return self.receive_end - self.start_time if self.receive_end > 0 else 0

    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式"""
        return {
            "dns_resolution": round(self.dns_time * 1000, 2),  # 转换为毫秒
            "tcp_connection": round(self.connect_time * 1000, 2),
            "ssl_handshake": round(self.ssl_time * 1000, 2),
            "request_send": round(self.send_time * 1000, 2),
            "response_receive": round(self.receive_time * 1000, 2),
            "total_time": round(self.total_time * 1000, 2)
        }

class TimingTracker:
    """请求耗时追踪器"""
    def __init__(self):
        self.timing = RequestTiming(start_time=time.time())

    async def track_dns_resolution(self, host: str) -> Tuple[str, float]:
        """追踪DNS解析耗时"""
        self.timing.dns_start = time.time()
        try:
            # 异步DNS解析
            loop = asyncio.get_event_loop()
            ip = await loop.run_in_executor(
                None, 
                socket.gethostbyname, 
                host
            )
            self.timing.dns_end = time.time()
            return ip, self.timing.dns_time
        except Exception as e:
            logger.error(f"DNS resolution failed: {str(e)}")
            self.timing.dns_end = time.time()
            raise

class HTTPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._session = None
        self._connector = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            # 创建带有TCP连接追踪的connector
            self._connector = aiohttp.TCPConnector(
                enable_cleanup_closed=True,
                force_close=True,
                ssl=ssl.create_default_context()
            )
            self._session = aiohttp.ClientSession(connector=self._connector)
        return self._session

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Union[Dict, str]:
        """解析响应内容"""
        content_type = response.headers.get('Content-Type', '')
        try:
            if 'application/json' in content_type:
                return await response.json()
            elif 'text/html' in content_type:
                return await response.text()
            else:
                return await response.text()
        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            return await response.text()

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        merged_headers = {**default_headers, **(headers or {})}
        
        # 创建耗时追踪器
        tracker = TimingTracker()
        
        try:
            # DNS解析
            from urllib.parse import urlparse
            host = urlparse(url).netloc
            await tracker.track_dns_resolution(host)
            
            # 记录请求信息
            logger.log_request(
                method=method,
                url=url,
                headers=merged_headers,
                params=params,
                data=json
            )
            
            # TCP连接和请求发送
            tracker.timing.connect_start = time.time()
            async with session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=merged_headers,
                **kwargs
            ) as response:
                tracker.timing.connect_end = time.time()
                
                # SSL/TLS握手时间（如果是HTTPS）
                if url.startswith('https'):
                    tracker.timing.ssl_start = tracker.timing.connect_end
                    tracker.timing.ssl_end = time.time()
                
                # 接收响应
                tracker.timing.receive_start = time.time()
                response_data = await self._parse_response(response)
                tracker.timing.receive_end = time.time()
                
                # 记录响应信息和耗时分析
                logger.log_response(
                    status_code=response.status,
                    response_data=response_data,
                    timing=tracker.timing.to_dict()
                )
                
                # 将解析后的数据附加到响应对象
                setattr(response, 'data', response_data)
                setattr(response, 'timing', tracker.timing)
                return response
                
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise
        finally:
            # 确保记录总耗时
            if tracker.timing.receive_end == 0:
                tracker.timing.receive_end = time.time()

    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()