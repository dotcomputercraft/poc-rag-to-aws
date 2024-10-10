import logging
import shutil
import sys
import os

sys.path.append('./rag_app')

from langchain_community.vectorstores import Chroma
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma
from get_embedding_function import get_embedding_function

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

CHROMA_PATH = os.environ.get("CHROMA_PATH", "data/chroma")
IS_USING_IMAGE_RUNTIME = bool(os.environ.get("IS_USING_IMAGE_RUNTIME", False))
CHROMA_DB_INSTANCE = None  # Reference to singleton instance of ChromaDB


def get_chroma_db():
    global CHROMA_DB_INSTANCE
    if not CHROMA_DB_INSTANCE:

        # Hack needed for AWS Lambda's base Python image (to work with an updated version of SQLite).
        # In Lambda runtime, we need to copy ChromaDB to /tmp so it can have write permissions.
        if IS_USING_IMAGE_RUNTIME:
            __import__("pysqlite3")
            sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
            copy_chroma_to_tmp()

        # Prepare the DB.
        CHROMA_DB_INSTANCE = Chroma(
            persist_directory=get_runtime_chroma_path(),
            embedding_function=get_embedding_function(),
        )
        LOGGER.info(f"Init ChromaDB {CHROMA_DB_INSTANCE} from {get_runtime_chroma_path()}")

    return CHROMA_DB_INSTANCE


def copy_chroma_to_tmp():
    dst_chroma_path = get_runtime_chroma_path()

    if not os.path.exists(dst_chroma_path):
        os.makedirs(dst_chroma_path)

    tmp_contents = os.listdir(dst_chroma_path)
    if len(tmp_contents) == 0:
        LOGGER.info(f"Copying ChromaDB from {CHROMA_PATH} to {dst_chroma_path}")
        os.makedirs(dst_chroma_path, exist_ok=True)
        shutil.copytree(CHROMA_PATH, dst_chroma_path, dirs_exist_ok=True)
    else:
        LOGGER.info(f"ChromaDB already exists in {dst_chroma_path}")


def get_runtime_chroma_path():
    if IS_USING_IMAGE_RUNTIME:
        return f"/tmp/{CHROMA_PATH}"
    else:
        return f"src/{CHROMA_PATH}"
