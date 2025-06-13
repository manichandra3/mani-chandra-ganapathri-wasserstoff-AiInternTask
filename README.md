# Document Processing API

A FastAPI-based backend service for processing documents with OCR capabilities. The service can handle PDFs, images, and text files, extract text using OCR when needed, and store the processed content in a structured format.

## Features

- Document upload and processing (PDF, images, text)
- OCR text extraction using Tesseract
- Structured storage of document content
- RESTful API endpoints
- SQLite database for metadata storage
- JSON export of processed documents

## Prerequisites

- Python 3.8+
- Tesseract OCR installed on your system
- Poppler (for PDF processing)

### Installing Tesseract OCR

#### Windows
1. Download the installer from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to default location (`C:\Program Files\Tesseract-OCR`)
3. Add Tesseract to your system PATH

#### Linux
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

### Installing Poppler

#### Windows
1. Download from [https://github.com/oschwartz10612/poppler-windows/releases/](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Extract to a location on your system
3. Add the `bin` directory to your system PATH

#### Linux
```bash
sudo apt-get install poppler-utils
```

#### macOS
```bash
brew install poppler
```

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create required directories:
```bash
mkdir -p data/uploads data/processed
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Upload Document
```
POST /api/v1/upload
```
Upload a document for processing. Supports PDF, images (JPG, PNG), and text files.

### List Documents
```
GET /api/v1/documents
```
List all processed documents.

### Get Document
```
GET /api/v1/documents/{document_id}
```
Get details and content of a specific document.

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
.
├── app/
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   ├── routers/
│   │   └── documents.py
│   ├── services/
│   │   └── document_processor.py
│   └── main.py
├── data/
│   ├── uploads/
│   └── processed/
├── requirements.txt
└── README.md
```

## License

MIT 