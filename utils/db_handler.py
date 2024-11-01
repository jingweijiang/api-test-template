from typing import Dict, List, Any, Optional
import pymysql
from pymongo import MongoClient
from config.settings import settings
from core.logger import logger

class MySQLHandler:
    def __init__(self):
        self.config = settings.db_config["mysql"]
        self.connection = None
        self._connect()

    def _connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.config["host"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                port=self.config["port"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            logger.error(f"MySQL connection failed: {str(e)}")
            raise

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """执行查询操作"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
        
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """执行更新操作"""
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params or ())
                self.connection.commit()
                return affected_rows
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Update execution failed: {str(e)}")
            raise

class MongoHandler:
    def __init__(self):
        self.config = settings.db_config["mongodb"]
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(
                host=self.config["host"],
                port=self.config["port"],
                username=self.config.get("username"),
                password=self.config.get("password")
            )
            self.db = self.client[self.config["database"]]
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise

    def find(self, collection: str, query: Dict = None, projection: Dict = None) -> List[Dict]:
        """查询文档"""
        return list(self.db[collection].find(query or {}, projection or {}))

    def insert_one(self, collection: str, document: Dict) -> str:
        """插入单个文档"""
        result = self.db[collection].insert_one(document)
        return str(result.inserted_id)

    def update_many(self, collection: str, filter_query: Dict, update_data: Dict) -> int:
        """更新多个文档"""
        result = self.db[collection].update_many(filter_query, {"$set": update_data})
        return result.modified_count

    def delete_many(self, collection: str, filter_query: Dict) -> int:
        """删除多个文档"""
        result = self.db[collection].delete_many(filter_query)
        return result.deleted_count 