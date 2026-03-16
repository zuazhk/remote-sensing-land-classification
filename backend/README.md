# Remote Sensing Image Classification API

Modern SPA version of the remote sensing image classification system.

## Features

- RESTful API for image classification
- Support for multiple deep learning models (EfficientNet-B0, Swin Transformer)
- Batch prediction and model evaluation
- Visualization endpoints for model performance analysis
- CORS enabled for frontend integration

## Installation

1. Create virtual environment:
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -e .
   ```

## Usage

Start the API server:
```bash
python -m backend.main
```

Or use uvicorn directly:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc

## Configuration

Edit `backend/config.py` to modify:
- Model paths
- API host/port
- CORS origins
- File upload limits

## License

MIT