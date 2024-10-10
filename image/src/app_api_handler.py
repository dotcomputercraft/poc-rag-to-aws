import os
import uvicorn
import json
import logging

import sys

from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from query_model import QueryModel
from rag_app.query_rag import query_rag


from lib.common import set_logging, get_lambda_client

LOGGER = logging.getLogger()
set_logging(LOGGER)

WORKER_LAMBDA_NAME = os.environ.get("WORKER_LAMBDA_NAME", None)

app = FastAPI()
handler = Mangum(app)  # Entry point for AWS Lambda.


class SubmitQueryRequest(BaseModel):
    query_text: str


@app.get("/")
def index():
    LOGGER.info("index invoked")
    
    return {"Hello": "World"}


@app.get("/get_query")
def get_query_endpoint(query_id: str) -> QueryModel:
    LOGGER.info(
        f"get_query_endpoint invoked. query_id - {query_id}")
    
    query = QueryModel.get_item(query_id)
    return query


@app.post("/submit_query")
def submit_query_endpoint(request: SubmitQueryRequest) -> QueryModel:
    LOGGER.info(
        f"submit_query_endpoint invoked. WORKER_LAMBDA_NAME - {WORKER_LAMBDA_NAME} - request - {request}")

    # Create the query item, and put it into the data-base.
    new_query = QueryModel(query_text=request.query_text)

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
