import os
import time
import uuid
import boto3
import logging
import traceback
import sys


from pydantic import BaseModel, Field
from typing import List, Optional
from botocore.exceptions import ClientError

from lib.common import get_boto3_session

db_region = os.environ.get('AWS_DEFAULT_REGION')
TABLE_NAME = os.environ.get('TABLE_NAME')
TTL_EXPIRE_MONTHS = 6  # Only keep queries for 6 months.
TTL_EXPIRE_TIMESTAMP = 60 * 60 * 24 * 30 * TTL_EXPIRE_MONTHS
GSI_INDEX_NAME = "queries_by_user_id"

from loguru import logger as LOGGER


class QueryModel(BaseModel):
    query_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    user_id: str = "nobody"
    create_time: int = Field(default_factory=lambda: int(time.time()))
    ttl: int = Field(default_factory=lambda: int(time.time() + TTL_EXPIRE_TIMESTAMP))
    query_text: str
    answer_text: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    is_complete: bool = False

    @classmethod
    def get_table(cls: "QueryModel") -> boto3.resource:
        """
        get_table() is the entry point to be invoked
        :param cls:
        """
        if os.getenv('IS_OFFLINE') == 'true':
            dynamodb = get_boto3_session().resource('dynamodb', endpoint_url='http://localhost:8000')
        else:
            dynamodb = get_boto3_session().resource('dynamodb', region_name=db_region)
        return dynamodb.Table(TABLE_NAME)

    def put_item(self):
        LOGGER.info(
            f"put_item invoked. db_region - {db_region} - TABLE_NAME - {TABLE_NAME}")  

        item = self.as_ddb_item()

        LOGGER.info(
            f"put_item self.as_ddb_item(): item: {item}")  

        try:
            response = QueryModel.get_table().put_item(Item=item)
            LOGGER.info(response)
        except ClientError as e:
            traceback.print_exc()
            LOGGER.error(e)            
            raise e

    def as_ddb_item(self):
        item = {k: v for k, v in self.dict().items() if v is not None}
        return item

    @classmethod
    def get_item(cls: "QueryModel", query_id: str) -> "QueryModel":
        LOGGER.info(
            f"get_item invoked. db_region: {db_region} - TABLE_NAME: {TABLE_NAME} - query_id: {query_id}")  
              
        try:
            response = cls.get_table().get_item(Key={"query_id": query_id})
        except ClientError as e:
            traceback.print_exc()
            LOGGER.error(e)            
            return None

        if "Item" in response:
            item = response["Item"]
            return cls(**item)
        else:
            return None

    @classmethod
    def list_items(cls: "QueryModel", user_id: str, count: int) -> list["QueryModel"]:
        LOGGER.info(
            f"list_items invoked. db_region: {db_region} - user_id: {user_id} - TABLE_NAME: {TABLE_NAME} - count: {count}")  

        try:
            response = cls.get_table().query(
                IndexName=GSI_INDEX_NAME,
                KeyConditionExpression="user_id = :user_id",
                ExpressionAttributeValues={":user_id": user_id},
                Limit=count,
                ScanIndexForward=False,
            )
        except ClientError as e:
            traceback.print_exc()
            LOGGER.error(e)             
            return []

        items = response.get("Items", [])
        return [cls(**item) for item in items]
