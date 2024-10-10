import sys
import logging
import os
import argparse


from dataclasses import dataclass
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock

sys.path.append('./rag_app')

from get_chroma_db import get_chroma_db

# You will also need to have Bedrock's model name enabled and granted for the region you are running this in.

BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

def set_logging(logger):
    # Setup Logging
    FORMAT = '%(lineno)s %(levelname)s:%(name)s %(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT)

    if os.getenv('STAGE') == 'dev' or os.getenv('VERBOSE', '').lower() in ('true', '1'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('nose').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


LOGGER = logging.getLogger()
set_logging(LOGGER)


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


@dataclass
class QueryResponse:
    query_text: str
    response_text: str
    sources: List[str]


def query_rag(query_text: str) -> QueryResponse:
    db = get_chroma_db()

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    LOGGER.info(prompt)

    model = ChatBedrock(model_id=BEDROCK_MODEL_ID)
    response = model.invoke(prompt)
    response_text = response.content

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    LOGGER.info(f"Response: {response_text}\nSources: {sources}")

    return QueryResponse(
        query_text=query_text, response_text=response_text, sources=sources
    )

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


if __name__ == "__main__":
    main()
