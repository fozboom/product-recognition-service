import json
import logging
import random
from pathlib import Path

import spacy
from spacy.training.example import Example

from product_recognition_service.logging_setup import setup_logging

TRAIN_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "spacy_training_data.json"
MODEL_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "models" / "product_ner_model_v2"
N_ITER = 50

logger = logging.getLogger(__name__)

def train_spacy_ner_model():
    """Trains a new spaCy NER model on the product data."""

    try:
        with open(TRAIN_DATA_PATH, 'r', encoding='utf-8') as f:
            TRAIN_DATA = json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: Training data file '{TRAIN_DATA_PATH}' not found.")
        logger.error("Please run the data preparation script first.")
        return
    except json.JSONDecodeError:
        logger.error(f"Error: Could not decode JSON from '{TRAIN_DATA_PATH}'.")
        return

    nlp = spacy.blank("en")
    logger.info("Created blank 'en' model")

    # Add the NER (Named Entity Recognition) component to the pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Add the "PRODUCT" label to the NER component
    # spaCy requires all labels to be added before training
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # 3. Train the model
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.select_pipes(disable=other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        logger.info("Starting training...")
        for itn in range(N_ITER):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # Batch up the examples using spaCy's minibatch
            batches = spacy.util.minibatch(TRAIN_DATA, size=32)
            for batch in batches:
                examples = []
                for text, annotations in batch:
                    examples.append(Example.from_dict(nlp.make_doc(text), annotations))
                # Update the model with the batch of examples
                nlp.update(
                    examples,
                    drop=0.1, 
                    sgd=optimizer,
                    losses=losses,
                )
            logger.info(f"Iteration {itn + 1}/{N_ITER}, Losses: {losses}")

    # 4. Save the trained model
    nlp.to_disk(MODEL_OUTPUT_DIR)
    logger.info(f"\nModel trained and saved to '{MODEL_OUTPUT_DIR}'")
    logger.info("You can now use this model to find product entities in your text.")

if __name__ == "__main__":
    setup_logging()
    print("Starting training...")
    train_spacy_ner_model() 