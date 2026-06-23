import os
import json
import re
import yaml
import pandas as pd
from PyPDF2 import PdfReader
from app.services.chunking_service import create_text_chunks
from app.services.vector_store_service import store_chunks_in_vector_db
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".csv", ".xlsx", ".xls", ".json", ".yaml", ".yml"]


def process_document(file_path: str):
    extension = os.path.splitext(file_path)[1].lower()

    validation_result = validate_document(file_path, extension)
    if validation_result["status"] == "failed":
        return validation_result

    raw_text = extract_raw_data(file_path, extension)
    cleaned_text = clean_data(raw_text)

    chunks = create_text_chunks(cleaned_text)

    vector_store_result = store_chunks_in_vector_db(
        chunks=chunks,
        filename=os.path.basename(file_path)
    )

    return {
        "status": "success",
        "filename": os.path.basename(file_path),
        "file_type": extension,
        "raw_characters": len(raw_text),
        "cleaned_characters": len(cleaned_text),
        "total_chunks": len(chunks),
        "sample_chunk": chunks[0] if chunks else "",
        "vector_store_status": vector_store_result["status"],
        "chunks_stored": vector_store_result.get("chunks_stored", 0),
        "collection_name": vector_store_result.get("collection_name", ""),
        "content_preview": cleaned_text[:500],
        "message": "Document ingested, cleaned, chunked, embedded, and stored successfully"
    }


def validate_document(file_path: str, extension: str):
    if not os.path.exists(file_path):
        return {"status": "failed", "message": "File does not exist"}

    if extension not in SUPPORTED_EXTENSIONS:
        return {"status": "failed", "message": f"Unsupported file type: {extension}"}

    if os.path.getsize(file_path) == 0:
        return {"status": "failed", "message": "File is empty"}

    if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
        return {
            "status": "failed",
            "message": f"File size exceeds {MAX_FILE_SIZE_MB} MB limit"
        }

    return {"status": "success", "message": "File validation successful"}


def extract_raw_data(file_path: str, extension: str):
    if extension == ".pdf":
        return extract_pdf(file_path)
    if extension == ".txt":
        return extract_txt(file_path)
    if extension == ".csv":
        return extract_csv(file_path)
    if extension in [".xlsx", ".xls"]:
        return extract_excel(file_path)
    if extension == ".json":
        return extract_json(file_path)
    if extension in [".yaml", ".yml"]:
        return extract_yaml(file_path)

    return ""


def extract_pdf(file_path: str):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_txt(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_csv(file_path: str):
    df = pd.read_csv(file_path)
    df = df.dropna(how="all")
    return df.to_string(index=False)


def extract_excel(file_path: str):
    df = pd.read_excel(file_path, engine="openpyxl")
    df = df.dropna(how="all")
    return df.to_string(index=False)


def extract_json(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)

        return json.dumps(data, indent=2)

    except json.JSONDecodeError as e:
        return f"Invalid JSON file. Error: {str(e)}"


def extract_yaml(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return yaml.dump(data, sort_keys=False)


def clean_data(text: str):

    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()