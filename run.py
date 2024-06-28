from helper import *
import mysql.connector
import random
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger()

RESEND_KEY = os.getenv("RESEND_KEY")
STRIPE_KEY = os.getenv("STRIPE_KEY")
MONDAY_KEY = os.getenv("MONDAY_KEY")
SLACK_KEY = os.getenv("SLACK_KEY")


def main():

    logging.basicConfig(
        format="%(message)s",
        handlers=[logging.StreamHandler(ColorPrint())],
    )
    logger.setLevel(logging.INFO)

    scenario = input("Please select a scenario (stripe,monday,slack,resend): ")

    scenario = scenario.lower()
    api_spec, headers = None, None

    if scenario == "resend":

        api_spec, headers = process_spec_file(
            file_path="specs/resend_oas.json", token=RESEND_KEY
        )

        headers["Content-Type"] = "application/json"

        query_example = 'Send an email to maxxii.2420@gmail.com with subject "Payment Link" and html "<p>Here is the payment link for the development: https://buy.stripe.com/test_biy4iu9dj2uyefw8wq</p>"'
    elif scenario == "stripe":

        api_spec, headers = process_spec_file(
            file_path="specs/stripe_oas.json", token=STRIPE_KEY
        )

        headers["Content-Type"] = "application/x-www-form-urlencoded"
        query_example = "Generate a payment link for price_1PS6FEBk0CUtnrfuZYMDDe1q"
    elif scenario == "slack":

        api_spec, headers = process_spec_file(
            file_path="specs/slack_oas.json", token=SLACK_KEY
        )

        headers["Content-Type"] = "application/x-www-form-urlencoded"
        query_example = "Send a message to the general channel saying 'hello guys'"
    elif scenario == "monday":

        api_spec, headers = process_spec_file(
            file_path="specs/monday_oas.json", token=MONDAY_KEY
        )

        headers["Content-Type"] = "application/json"

        query_example = (
            "Get the total duration of my tasks in monday for the board agileloop"
        )
    else:
        raise ValueError(f"Unsupported scenario: {scenario}")

    populate_api_selector_icl_examples(scenario=scenario)
    populate_planner_icl_examples(scenario=scenario)

    requests_wrapper = Requests(headers=headers)

    # text-davinci-003

    llm = OpenAI(model_name="gpt-4o", temperature=0.0, max_tokens=1024)
    api_llm = ApiLLM(
        llm,
        api_spec=api_spec,
        scenario=scenario,
        requests_wrapper=requests_wrapper,
        simple_parser=False,
    )

    print(f"Example instruction: {query_example}")
    query = input(
        "Please input an instruction (Press ENTER to use the example instruction): "
    )
    if query == "":
        query = query_example

    logger.info(f"Query: {query}")

    start_time = time.time()
    api_llm.run(query)
    logger.info(f"Execution Time: {time.time() - start_time}")


if __name__ == "__main__":
    main()
