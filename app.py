import os
import sys

import certifi
import pandas as pd
import pymongo
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from networksecuirty.constant.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME,
)
from networksecuirty.exception.exception import NetworkSecurityException
from networksecuirty.logging.logger import logging
from networksecuirty.pipeline.training_pipeline import TrainingPipeline
from networksecuirty.utils.main_utils.utils import load_object
from networksecuirty.utils.ml_utils.model.estimator import NetworkModel
from uvicorn import run as app_run

load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
ca = certifi.where()

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]
templates = Jinja2Templates(directory="./templates")
app.mount("/static", StaticFiles(directory="./static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FEATURE_COLUMNS = [
    "having_IP_Address",
    "URL_Length",
    "Shortining_Service",
    "having_At_Symbol",
    "double_slash_redirecting",
    "Prefix_Suffix",
    "having_Sub_Domain",
    "SSLfinal_State",
    "Domain_registeration_length",
    "Favicon",
    "port",
    "HTTPS_token",
    "Request_URL",
    "URL_of_Anchor",
    "Links_in_tags",
    "SFH",
    "Submitting_to_email",
    "Abnormal_URL",
    "Redirect",
    "on_mouseover",
    "RightClick",
    "popUpWidnow",
    "Iframe",
    "age_of_domain",
    "DNSRecord",
    "web_traffic",
    "Page_Rank",
    "Google_Index",
    "Links_pointing_to_page",
    "Statistical_report",
]

FEATURE_HINT = "Numeric dataset value: -1, 0, or 1."
PREDICTION_LABELS = {0: "Phishing", 1: "Legitimate", -1: "Phishing"}


def _feature_context():
    return {
        "features": [
            {"name": name, "hint": FEATURE_HINT} for name in FEATURE_COLUMNS
        ]
    }


def _error_response(message: str, status_code: int):
    logging.error(message)
    return JSONResponse(status_code=status_code, content={"detail": message})


def _prepare_prediction(df: pd.DataFrame):
    missing_columns = [column for column in FEATURE_COLUMNS if column not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail="Missing required columns: " + ", ".join(missing_columns),
        )

    input_df = df[FEATURE_COLUMNS]
    numeric_df = input_df.apply(pd.to_numeric, errors="coerce")
    invalid_values = numeric_df.isna() & input_df.notna()
    if invalid_values.any().any():
        invalid_columns = invalid_values.any(axis=0)
        columns = list(invalid_columns[invalid_columns].index)
        raise HTTPException(
            status_code=400,
            detail="Non-numeric values found in: " + ", ".join(columns),
        )
    if numeric_df.isna().any().any():
        raise HTTPException(
            status_code=400,
            detail="Missing values are not allowed in the feature columns.",
        )

    try:
        preprocessor = load_object("final_model/preprocessor")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(
            preprocessor=preprocessor, model=final_model
        )
        predictions = network_model.predict(numeric_df.to_numpy(dtype=float))
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

    predictions = [int(value) for value in predictions]
    labels = [PREDICTION_LABELS.get(value, str(value)) for value in predictions]
    output_df = df.copy()
    output_df["predicted_column"] = predictions
    output_df["prediction_label"] = labels
    os.makedirs("prediction_output", exist_ok=True)
    output_df.to_csv("prediction_output/output.csv", index=False)

    rows = output_df.where(pd.notna(output_df), None).to_dict(orient="records")
    summary = {
        "phishing": labels.count("Phishing"),
        "legitimate": labels.count("Legitimate"),
        "total": len(labels),
    }
    return {
        "columns": list(output_df.columns),
        "rows": rows,
        "predictions": predictions,
        "summary": summary,
    }


@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/ui")


@app.get("/ui", include_in_schema=False)
async def ui_home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )


@app.get("/model", include_in_schema=False)
async def model_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="model.html",
        context={"request": request, **_feature_context()},
    )


@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return {"message": "Training is successful."}
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


@app.post("/predict")
async def predict_route(file: UploadFile = File(...)):
    if not file.filename:
        return _error_response("Please select a CSV file.", 400)
    if not file.filename.lower().endswith(".csv"):
        return _error_response("Please upload a CSV file.", 400)

    try:
        df = pd.read_csv(file.file)
        if df.empty:
            return _error_response("The uploaded CSV has no data rows.", 400)
        return _prepare_prediction(df)
    except HTTPException as e:
        return _error_response(str(e.detail), e.status_code)
    except pd.errors.ParserError:
        return _error_response("The uploaded file is not a valid CSV.", 400)
    except NetworkSecurityException:
        raise
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


@app.get("/download-predictions", include_in_schema=False)
async def download_predictions():
    output_path = "prediction_output/output.csv"
    if not os.path.exists(output_path):
        return _error_response("Run a prediction before downloading results.", 404)
    return FileResponse(
        output_path,
        media_type="text/csv",
        filename="predictions.csv",
    )


if __name__ == "__main__":
    app_run(app, host="localhost", port=8000)
