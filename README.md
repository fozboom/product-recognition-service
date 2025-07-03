# Product Recognition Service

This project is a web service for extracting product names from furniture store websites using a Named Entity Recognition (NER) model.

## 🚀 Getting Started

You can run this project locally for development or use Docker for a containerized setup.

### Prerequisites

- [Python 3.12+](https://www.python.org/)
- [Docker](https.://www.docker.com/) (optional)

### Local Development

1.  **Install `uv`:**

    `uv` is an extremely fast Python package and project manager. Install it using the recommended method for your OS:

    -   **macOS / Linux:**
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
    -   **Windows:**
        ```powershell
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```
    After installation, ensure your shell is configured to use `uv` by following the instructions printed in your terminal.

2.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd product-recognition-service
    ```

3.  **Install dependencies:**

    Sync the virtual environment with the project's locked dependencies. This command ensures a consistent setup by installing the exact versions specified in `pyproject.toml` and `uv.lock`.
    
    ```bash
    uv sync
    ```

4.  **Run the application:**

    The application is a FastAPI service. Run it with `uvicorn` (through `uv`):

    ```bash
    uv run uvicorn src.product_recognition_service.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The `--reload` flag enables hot-reloading for development. The service will be available at [http://localhost:8000](http://localhost:8000).

### Docker Setup

1.  **Build the Docker image:**
    ```bash
    docker build -t ml-edidantix-task .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 ml-edidantix-task
    ```
    The service will be available at [http://localhost:8000](http://localhost:8000).

## 🧠 Training the Model

Before running the application, you may need to train the Named Entity Recognition (NER) model.

1.  **Prepare the training data:**
    
    Ensure that your processed training data is available at `data/processed/spacy_training_data.json`. You might need to run a data preparation script first if it's not present.

2.  **Run the training script:**
    ```bash
    uv run python src/scripts/train.py
    ```
    This script will train a new spaCy model and save it to the `models/product_ner_model` directory. The trained model will then be used by the application.

## 📂 Project Structure
-   `data` - Contains data files, such as the list of URLs for parsing and processed data
-   `src/`: Main source code.
    -   `product_recognition_service/`: The core FastAPI application for product recognition.
    -   `scripts/`: Helper scripts for tasks like training the model, processing data, etc.
    -   `templates/`: HTML templates for the web interface.
-   `tests/`: Contains tests for the application (mannual)
-   `Dockerfile`: Defines the Docker image for the application.
-   `pyproject.toml`: Project metadata and dependencies.