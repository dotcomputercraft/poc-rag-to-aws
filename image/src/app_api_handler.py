import os
from typing import Optional
import uvicorn
import json
import logging

import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from mangum import Mangum
from pydantic import BaseModel
from query_model import QueryModel
from rag_app.query_rag import query_rag


from lib.common import get_lambda_client

from loguru import logger as LOGGER

WORKER_LAMBDA_NAME = os.environ.get("WORKER_LAMBDA_NAME", None)
CHARACTER_LIMIT = 2000

app = FastAPI()

# Configure CORS so that the frontend can access this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

handler = Mangum(app)  # Entry point for AWS Lambda.

class SubmitQueryRequest(BaseModel):
    query_text: str
    user_id: Optional[str] = None


@app.get("/")
def index():
    LOGGER.info("index invoked")
    
    return {"Hello": "World"}


@app.get("/get_query")
def get_query_endpoint(query_id: str) -> QueryModel:
    LOGGER.info(
        f"get_query_endpoint invoked. query_id - {query_id}")
    
    query = QueryModel.get_item(query_id)
    if query:
        return query
    else:
        raise HTTPException(status_code=404, detail=f"Query Not Found: {query_id}")

@app.get("/list_query")
def list_query_endpoint(user_id: str) -> list[QueryModel]:
    ITEM_COUNT = 25
    LOGGER.info(f"Listing queries for user: {user_id}")
    query_items = QueryModel.list_items(user_id=user_id, count=ITEM_COUNT)
    return query_items

@app.post("/submit_query")
def submit_query_endpoint(request: SubmitQueryRequest) -> QueryModel:
    LOGGER.info(
        f"submit_query_endpoint invoked. WORKER_LAMBDA_NAME - {WORKER_LAMBDA_NAME} - request - {request}")

    # Check if the query is too long.
    if len(request.query_text) > CHARACTER_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"Query is too long. Max character limit is {CHARACTER_LIMIT}",
        )

    # Create the query item, and put it into the data-base.
    user_id = request.user_id if request.user_id else "nobody"
    new_query = QueryModel(query_text=request.query_text, user_id=user_id)

    LOGGER.info(
        f"submit_query_endpoint new_query: {new_query} - request: {request}")

    if WORKER_LAMBDA_NAME:
        LOGGER.info(f"submit_query_endpoint - Worker lambda name provided. WORKER_LAMBDA_NAME - {WORKER_LAMBDA_NAME}. Running asynchronously.")
        # Make an async call to the worker (the RAG/AI app).
        new_query.put_item()
        invoke_worker(new_query)
    else:
        LOGGER.info("submit_query_endpoint - No worker lambda name provided. Running synchronously.")
        # Make a synchronous call to the worker (the RAG/AI app).
        query_response = query_rag(request.query_text)
        new_query.answer_text = query_response.response_text
        new_query.sources = query_response.sources
        new_query.is_complete = True
        new_query.put_item()

    return new_query


def invoke_worker(query: QueryModel):
    LOGGER.info(
        f"lambda_handler invoked. query - {query}")

    # Initialize the Lambda client
    lambda_client = get_lambda_client()

    # Get the QueryModel as a dictionary.
    payload = query.model_dump()

    # Invoke another Lambda function asynchronously
    response = lambda_client.invoke(
        FunctionName=WORKER_LAMBDA_NAME,
        InvocationType="Event",
        Payload=json.dumps(payload),
    )

    LOGGER.info(f"Worker Lambda invoked: {response}")


if __name__ == "__main__":
    # Run this as a server directly.
    port = 8000
    LOGGER.info(f"Running the FastAPI server on port {port}.")
    uvicorn.run("app_api_handler:app", host="0.0.0.0", port=port)
