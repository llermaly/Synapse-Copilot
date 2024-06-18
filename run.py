from helper import *
import mysql.connector
import random
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger()


def main():

    logging.basicConfig(
        format="%(message)s",
        handlers=[logging.StreamHandler(ColorPrint())],
    )
    logger.setLevel(logging.INFO)

    scenario = input("Please select a scenario (stripe): ")

    scenario = scenario.lower()
    api_spec, headers = None, None

    # database connection details
    db_config = {
        "host": "localhost",
        "database": "synapse-copilot",
        "user": "root",
        "password": "",
    }

    # Connect to the MySQL server
    # conn = mysql.connector.connect(**db_config)
    # cursor = conn.cursor()

    # user_id = int(input("Enter the user id: "))

    if scenario == "stripe":

        api_spec, headers = process_spec_file(
            file_path="specs/stripe_oas.json", token=os.getenv["STRIPE_KEY"]
        )

        headers["Content-Type"] = "application/x-www-form-urlencoded"
        query_example = "Generate a payment link for price_1PS6FEBk0CUtnrfuZYMDDe1q"
    elif scenario == "monday":

        api_spec, headers = process_spec_file(
            file_path="specs/monday_oas.json", token=os.getenv("MONDAY_KEY")
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
