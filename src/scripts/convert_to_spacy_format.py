import json
from datetime import datetime
from pathlib import Path


def convert_to_spacy_format(input_path: Path, output_path: Path):
    """
    Converts annotation data into the simple spaCy training format.

    This function performs a direct conversion, trusting that the input
    entity offsets are correct and non-overlapping.

    Input format:
    [
        {
            "source_url": "https://www.apple.com",
            "text": "Apple is a company.",
            "entits": [{"start": 0, "end": 5, "label": "ORG", "text": "Apple"}]
        },
        ...
    ]

    Output format (for spaCy 3.0+):
    [
        ("Apple is a company.", {"entities": [[0, 5, "ORG"]]})
    ]
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading data from '{input_path}': {e}")
        return

    spacy_training_data = []
    for entry in data:
        text = entry.get("text")
        entities_list = entry.get("entities")
        if not text or not isinstance(entities_list, list):
            continue

        spacy_entities = []
        for entity in entities_list:
            start = entity.get("start")
            end = entity.get("end")
            label = entity.get("label")
            if start is not None and end is not None and label:
                spacy_entities.append((start, end, label))

        spacy_training_data.append((text, {"entities": spacy_entities}))

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(spacy_training_data, f, indent=4, ensure_ascii=False)
        print(f"Successfully converted {len(spacy_training_data)} entries.")
        print(f"Output saved to '{output_path}'")

    except IOError as e:
        print(f"Error: Could not write data to file '{output_path}': {e}")


if __name__ == "__main__":
    # By default, this script will look for 'new_annotation_data_22_entries.json'
    # in the same directory and create 'spacy_training_data.json'.
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "data" / "processed" / "labeled_data.json"
    output_path = project_root / "data" / "processed" / f"spacy_training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    convert_to_spacy_format(input_path, output_path)
