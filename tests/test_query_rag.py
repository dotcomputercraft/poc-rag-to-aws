from image.src.rag_app.query_rag import query_rag

from loguru import logger as LOGGER

def test_design_client_guide_question1():
    assert query_and_validate(
        question="how much does a landing page cost? (Answer with the number only)",
        expected_response="$4,820",
    )

def test_design_client_guide_question2():
    assert not query_and_validate(
        question="how much does a landing page cost? (Answer with the number only)",
        expected_response="$4,800",
    )

def test_monopoly_rules():
    assert not query_and_validate(
        question="How much total money does a player start with in Monopoly? (Answer with the number only)",
        expected_response="$1500",
    )

def test_ticket_to_ride_question():
    assert query_and_validate(
        question="How many points does the longest continuous train get in Ticket to Ride? (Answer with the number only)",
        expected_response="15",
    )

def query_and_validate(question: str, expected_response: str):
    
    raw_results = query_rag(question)
    LOGGER.info(f"raw_results: {raw_results}")
   
    evaluation_results_str_cleaned = raw_results.response_text.lower().strip()

    LOGGER.info(f"expected_response: {expected_response}")
    LOGGER.info(f"evaluation_results_str: {evaluation_results_str_cleaned}")

    if  expected_response in evaluation_results_str_cleaned:
        # Print response in Green if it is correct.
        LOGGER.info("Print response in Green if it is correct.")
        LOGGER.info("\033[92m" + f"Response: {evaluation_results_str_cleaned}" + "\033[0m")
        return True
    elif expected_response not in evaluation_results_str_cleaned:
        # Print response in Red if it is incorrect.
        LOGGER.info("Print response in Red if it is incorrect.")
        LOGGER.info("\033[91m" + f"Response: {evaluation_results_str_cleaned}" + "\033[0m")
        return False
    else:
        raise ValueError(
            f"Invalid evaluation result. Cannot determine if 'true' or 'false'."
        )
