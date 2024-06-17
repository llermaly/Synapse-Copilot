from fastapi import FastAPI
from helper import *
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_KEY = os.getenv("STRIPE_KEY")

logger = logging.getLogger()

app = FastAPI()


class QueryData(BaseModel):
    query: str


@app.post("/query")
def run_query(data: QueryData):
    return {"result": stripe_scenario(data.query)}


def stripe_scenario(query: str):
    api_spec, headers = process_spec_file(
        file_path="specs/stripe_oas.json", token=STRIPE_KEY
    )

    headers["Content-Type"] = "application/x-www-form-urlencoded"

    populate_api_selector_icl_examples(scenario="stripe")
    populate_planner_icl_examples(scenario="stripe")

    requests_wrapper = Requests(headers=headers)

    llm = OpenAI(model_name="gpt-4o", temperature=0.0, max_tokens=1024)

    api_llm = ApiLLM(
        llm,
        api_spec=api_spec,
        scenario="stripe",
        requests_wrapper=requests_wrapper,
        simple_parser=False,
    )

    logger.info(f"Query: {query}")

    start_time = time.time()

    result = api_llm.run(query)

    logger.info(f"Execution Time: {time.time() - start_time}")

    return result
