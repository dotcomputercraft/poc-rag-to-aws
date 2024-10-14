import logging
from query_model import QueryModel
from rag_app.query_rag import query_rag

from lib.common import set_logging

from loguru import logger as LOGGER


def handler(event, context):
    LOGGER.info(
        f"handler invoked. event - {event}, context - {context}")

    query_item = QueryModel(**event)
    invoke_rag(query_item)


def invoke_rag(query_item: QueryModel):
    LOGGER.info(
        f"invoke_rag invoked. query_item - {query_item}")
    
    rag_response = query_rag(query_item.query_text)
    query_item.answer_text = rag_response.response_text
    query_item.sources = rag_response.sources
    query_item.is_complete = True
    query_item.put_item()
    LOGGER.info(f"Item is updated: {query_item}")
    return query_item


def main():
    LOGGER.info("main - Running example RAG call.")
    query_item = QueryModel(
        query_text="How long does an e-commerce system take to build?"
    )
    response = invoke_rag(query_item)
    LOGGER.info(f"Received: {response}")


if __name__ == "__main__":
    # For local testing.
    main()
