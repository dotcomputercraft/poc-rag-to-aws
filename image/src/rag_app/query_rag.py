import sys
import os
import argparse

# Add Parent Directory Programmatically
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dataclasses import dataclass
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock

from rag_app.get_chroma_db import get_chroma_db

from loguru import logger as LOGGER

# You will also need to have Bedrock's model name enabled and granted for the region you are running this in.

BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"


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
     # For local testing.
    LOGGER.info("main() invoked - query_rag.py - For local testing.")
    main()
