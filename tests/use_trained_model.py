import json
import random

import spacy

# Directory where the trained model is saved
MODEL_DIR = "product_ner_model"
# Path to the prepared annotated data
DATA_PATH = "spacy_training_data3.json" 

def evaluate_on_annotated_data(sample_index=None):
    """
    Loads the trained model, picks an example from the annotated data,
    and compares the model's predictions with the ground truth annotations.
    """
    # 1. Load the trained model
    print(f"Loading model from '{MODEL_DIR}'...")
    try:
        nlp = spacy.load(MODEL_DIR)
        print("Model loaded successfully.")
    except IOError:
        print(f"Error: Could not load model from '{MODEL_DIR}'.")
        print("Please make sure you have trained the model first.")
        return

    # 2. Load the annotated data
    print(f"Loading data from '{DATA_PATH}'...")
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading data: {e}")
        return

    # 3. Select an example to test
    if sample_index is not None and 0 <= sample_index < len(data):
        test_example = data[sample_index]
        print(f"\nUsing specified example #{sample_index}")
    else:
        test_example = random.choice(data)
        print("\nUsing a random example from the dataset...")
        
    text_to_analyze, annotations = test_example
    ground_truth_entities = annotations['entities']

    # 4. Process the text with the model to get predictions
    doc = nlp(text_to_analyze)

    # 5. Display the results for comparison
    print("\n" + "="*50)
    print("ANALYZING TEXT (first 500 chars):")
    print(f"'{text_to_analyze[:500]}...'")
    print("="*50)

    print("\n>>> MODEL PREDICTIONS:")
    if doc.ents:
        print(f"Found {len(doc.ents)} product(s):")
        for ent in doc.ents:
            print(f"- '{ent.text}' (Label: {ent.label_})")
    else:
        print("No products found by the model.")

    print("\n>>> GROUND TRUTH (Original Annotation):")
    if ground_truth_entities:
        print(f"Originally annotated {len(ground_truth_entities)} product(s):")
        for start, end, label in ground_truth_entities:
            print(f"- '{text_to_analyze[start:end]}' (Label: {label})")
    else:
        print("No products in the original annotation.")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    # Run the evaluation on a random sample.
    # You can also specify an index to check a specific example, 
    # e.g., evaluate_on_annotated_data(sample_index=10)
    evaluate_on_annotated_data() 