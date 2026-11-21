# Network Security

Network Security is a Python machine-learning application for identifying
phishing and legitimate websites from 30 URL and webpage signals. It includes
a FastAPI web interface, CSV batch predictions, manual single-row predictions,
and a training pipeline.

## Features

- Browser UI at `/ui` for CSV uploads and manual predictions
- JSON prediction endpoint at `POST /predict`
- Downloadable results at `/download-predictions`
- Model retraining from the bundled dataset or MongoDB
- Timestamped pipeline artifacts under `Artifacts/`
- Optional MongoDB data ingestion and S3 artifact/model backups

## Requirements

- Python 3.12 or later
- `pip`
- Optional: MongoDB connection string for remote data ingestion
- Optional: AWS CLI credentials for the S3 backup step in the training pipeline

## Installation

```bash
git clone <repository-url>
cd NetworkSecuirty

python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root when using MongoDB:

```dotenv
MONGO_DB_URL=mongodb+srv://<username>:<password>@<cluster>/<database>
```

If `MONGO_DB_URL` is not set, training falls back to
`Network_Data/phisingData.csv`. The application uses the `sample_mflix`
database and `NetworkData` collection when MongoDB is configured.

## Run the web application

Start the development server:

```bash
uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/> and select **Model Project**. You can upload a
CSV, enter one feature row manually, view row-level predictions, and download
the generated `prediction_output/output.csv` file.

The application labels predictions as:

- `0` or `-1`: **Phishing**
- `1`: **Legitimate**

## Input CSV format

The uploaded CSV must contain these 30 numeric feature columns. Values are
normally encoded as `-1`, `0`, or `1`; an optional `Result` target column is
preserved but is not required for prediction.

```text
having_IP_Address,URL_Length,Shortining_Service,having_At_Symbol,
double_slash_redirecting,Prefix_Suffix,having_Sub_Domain,SSLfinal_State,
Domain_registeration_length,Favicon,port,HTTPS_token,Request_URL,
URL_of_Anchor,Links_in_tags,SFH,Submitting_to_email,Abnormal_URL,Redirect,
on_mouseover,RightClick,popUpWidnow,Iframe,age_of_domain,DNSRecord,
web_traffic,Page_Rank,Google_Index,Links_pointing_to_page,Statistical_report
```

## API

### `POST /predict`

Upload a CSV as the `file` multipart field:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -F "file=@Network_Data/phisingData.csv"
```

The response contains the output columns, predicted values, row data, and a
summary of phishing and legitimate results.

### `GET /download-predictions`

Downloads the most recent prediction file. Run `/predict` first; otherwise the
endpoint returns `404`.

### `GET /train`

Runs data ingestion, validation, transformation, and model training. The
pipeline writes local artifacts and then synchronizes them to the configured
S3 bucket. Use this endpoint only when the required AWS configuration is
available.

## Run with Docker

Build and start the application:

```bash
docker build -t network-security .
docker run --rm -p 8000:8000 --env-file .env network-security
```

Then open <http://127.0.0.1:8000/>.

## Project layout

```text
app.py                         FastAPI application and prediction routes
main.py                        Component-by-component training entry point
push_data.py                   Optional CSV-to-MongoDB loader
networksecuirty/components/   Ingestion, validation, transformation, training
networksecuirty/pipeline/     End-to-end training pipeline
Network_Data/                  Bundled training dataset
final_model/                   Model and preprocessor used for prediction
prediction_output/             Latest generated predictions
Artifacts/                     Timestamped training artifacts
templates/ and static/         Web UI
```

## Troubleshooting

- **Missing model files:** run the training pipeline or restore
  `final_model/model.pkl` and `final_model/preprocessor`.
- **CSV validation errors:** verify every required feature column is present
  and contains numeric values without blanks.
- **MongoDB connection problems:** remove `MONGO_DB_URL` to use the bundled
  dataset, or verify the connection string and network access.
- **Upload errors:** ensure `python-multipart` is installed and the file has a
  `.csv` extension.
