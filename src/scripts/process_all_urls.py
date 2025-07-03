import csv
import json
import multiprocessing
from functools import partial
from pathlib import Path

from product_recognition_service.url_processor import URLProcessor


def process_single_url(url: str, html_dir: Path, text_dir: Path) -> tuple[bool, str, str | None]:
    """
    Processes a single URL. This function is designed to be called by a worker process.

    Args:
        url: The URL string to process.
        html_dir: The directory where the HTML file will be saved.
        text_dir: The directory where the extracted text file will be saved.

    Returns:
        A tuple containing:
        - bool: True if the URL was processed successfully, False otherwise.
        - str: The original URL.
        - str | None: The extracted text if successful, otherwise None.
    """
    try:
        processor = URLProcessor(url=url, html_output_dir=html_dir, text_output_dir=text_dir)
        if processor.process():
            return True, url, processor.text_content
        return False, url, None
    except Exception:
        # logger.error(f"An unexpected error occurred for URL {url}: {e}", exc_info=True)
        return False, url, None


def read_urls_from_csv(file_path: Path) -> list[str]:
    """
    Reads a CSV file from a given path and returns a clean list of URLs.

    Args:
        file_path: The Path object pointing to the CSV file.

    Returns:
        A list of URL strings. Returns an empty list if the file is not found or is empty.
    """
    if not file_path.is_file():
        print(f"CSV file not found at: {file_path}")
        return []

    urls = []
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip the header row
            for row in reader:
                if row and row[0].strip():
                    urls.append(row[0].strip())
    except IOError as e:
        print(f"Could not read CSV file {file_path}: {e}")
        return []

    print(f"Found {len(urls)} URLs in '{file_path.name}'.")
    return urls


def save_to_json(data: list[dict], output_file: Path):
    """
    Save the annotation data to a JSON file.

    Args:
        data: List of annotation entries.
        output_file: Path to the output JSON file.
    """
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} entries to {output_file}")
    except IOError as e:
        print(f"Could not write to JSON file {output_file}: {e}")


def process_all_urls(urls: list[str], html_dir: Path, text_dir: Path, annotation_file: Path):
    """
    Processes a list of URLs, saving their HTML and extracted text content.

    Args:
        urls: A list of URL strings to process.
        html_dir: The directory where HTML files will be saved.
        text_dir: The directory where extracted text files will be saved.
        annotation_file: The path to save the JSON file for annotation.
    """
    if not urls:
        print("URL list is empty. Nothing to process.")
        return

    # Ensure output directories exist before starting the loop
    html_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    print(f"HTML output will be saved to: {html_dir}")
    print(f"Text output will be saved to: {text_dir}")

    total_urls = len(urls)

    task_processor = partial(process_single_url, html_dir=html_dir, text_dir=text_dir)

    with multiprocessing.Pool() as pool:
        results = pool.map(task_processor, urls)

    success_count = 0
    annotation_data = []
    for success, url, text in results:
        if success and text:
            success_count += 1
            annotation_data.append({"source_url": url, "text": text, "entits": []})

    failure_count = total_urls - success_count

    print("--- URL Processing Complete ---")
    print(f"Successfully processed: {success_count}/{total_urls}")
    print(f"Failed to process:     {failure_count}/{total_urls}")

    if annotation_data:
        save_to_json(annotation_data, annotation_file)


def main():
    project_root = Path(__file__).resolve().parents[2]
    csv_file_path = project_root / "data" / "URL_list.csv"
    html_output_dir = project_root / "data" / "html_pages"
    text_output_dir = project_root / "data" / "text_content"
    print("Starting")
    urls_to_process = read_urls_from_csv(csv_file_path)
    if urls_to_process:
        output_file = project_root / f"new_annotation_data_{len(urls_to_process)}_entries.json"
        process_all_urls(urls_to_process, html_output_dir, text_output_dir, output_file)


if __name__ == "__main__":
    main()
