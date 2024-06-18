from fastapi import FastAPI
from helper import *
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_KEY = os.getenv("STRIPE_KEY")
MONDAY_KEY = os.getenv("MONDAY_KEY")
logger = logging.getLogger()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryData(BaseModel):
    query: str


@app.get("/ping")
def ping():
    return {"ok": True}


@app.post("/query")
def run_query(data: QueryData):
    scenario = None

    if "stripe" in data.query.lower():
        scenario = "stripe"
    elif "monday" in data.query.lower():
        scenario = "monday"
    else:
        return {
            "result": "Unsupported scenario, please specify either stripe or monday"
        }

    return {"result": run_scenario(data.query, scenario=scenario)}


def run_scenario(query: str, scenario: str):
    if scenario == "stripe":
        api_spec, headers = process_spec_file(
            file_path="specs/stripe_oas.json", token=STRIPE_KEY
        )

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif scenario == "monday":

        api_spec, headers = process_spec_file(
            file_path="specs/monday_oas.json", token=MONDAY_KEY
        )

        headers["Content-Type"] = "application/json"
    else:
        return "Unsupported scenario"

    populate_api_selector_icl_examples(scenario=scenario)
    populate_planner_icl_examples(scenario=scenario)

    requests_wrapper = Requests(headers=headers)

    llm = OpenAI(model_name="gpt-4o", temperature=0.0, max_tokens=1024)

    api_llm = ApiLLM(
        llm,
        api_spec=api_spec,
        scenario=scenario,
        requests_wrapper=requests_wrapper,
        simple_parser=False,
    )

    logger.info(f"Query: {query}")

    start_time = time.time()

    result = api_llm.run(query)

    logger.info(f"Execution Time: {time.time() - start_time}")

    return result
