import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import spacy
import uvicorn
import yaml
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings
from spacy.language import Language
from url_processor import URLProcessor

# Get logger with a specific name that matches the one in logging_config.yaml
logger = logging.getLogger("src.product_recognition_service.main")

class Settings(BaseSettings):
    """Manages application settings using Pydantic."""
    model_dir: Path = Path(__file__).resolve().parents[2] / "models" / "product_ner_model"
    templates_dir: Path = Path(__file__).resolve().parents[1] / "templates"

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    Loads the spaCy model on startup.
    """
    logger.info("Application startup...")
    try:
        if settings.model_dir.exists():
            app.state.nlp = spacy.load(settings.model_dir)
            logger.info(f"Model loaded successfully from '{settings.model_dir}'.")
        else:
            app.state.nlp = None
            logger.error(f"Model directory not found at '{settings.model_dir}'. The '/extract' endpoint will be unavailable.")
    except Exception as e:
        app.state.nlp = None
        logger.exception(f"Error loading model: {e}")
    
    yield
    
    logger.info("Application shutdown...")
# --- FastAPI App Initialization ---
app = FastAPI(
    title="Product Extractor API",
    description="Extracts product names from a given URL using a custom NER model.",
    version="1.0.0",
    lifespan=lifespan
)

templates = Jinja2Templates(directory=settings.templates_dir)

def get_nlp() -> Language:
    """
    Dependency to get the loaded spaCy model.
    Raises an HTTPException if the model is not available.
    """
    if not app.state.nlp:
        raise HTTPException(
            status_code=503, 
            detail="Model is not loaded. Please check server logs."
        )
    return app.state.nlp

NLP_DEPENDENCY = Annotated[Language, Depends(get_nlp)]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/extract")
async def extract_products(
    nlp: NLP_DEPENDENCY,
    url: str = Form(...)
):
    """Receives a URL, extracts text, and returns product entities."""
    try:
        url_processor = URLProcessor(url)
        text = url_processor.extract_text_from_url()
        if not text:
            raise HTTPException(
                status_code=400,
                detail="Could not retrieve or extract text from the URL. It might be down or blocking requests."
            )
        logger.debug(f"Extracted text: {text}")

        doc = nlp(text)
        products = list(set([ent.text for ent in doc.ents if ent.label_ == "PRODUCT"]))
        
        return JSONResponse(content={"products": products})
    except HTTPException as http_exc:
        logger.warning(f"Handled exception for URL '{url}': {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.exception(f"An unexpected error occurred while processing URL '{url}': {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


if __name__ == "__main__":
    # Load logging configuration from YAML file
    log_config_path = Path(__file__).resolve().parents[2] / "logging_config.yaml"
    log_config = None
    if log_config_path.exists():
        with open(log_config_path, 'r') as f:
            log_config = yaml.safe_load(f)

    logger.info("Starting Uvicorn server...")
    logger.info("Visit http://127.0.0.1:8000 in your browser.")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True, 
        log_config=log_config
    )