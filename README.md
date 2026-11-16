## Web UI

Start the FastAPI application from the project environment:

```bash
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/` and choose **Model Project**. Upload a CSV matching the training feature columns, or enter one website manually. Click **Predict** to view row-level phishing/legitimate labels and download the generated predictions CSV.