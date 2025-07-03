import yaml
import logging.config
import os

def setup_logging(default_path='logging_config.yaml', default_level=logging.INFO):
    """
    Setup logging configuration
    """
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(f"Error loading logging config: {e}")
                logging.basicConfig(level=default_level)
    else:
        print("logging_config.yaml not found. Using basicConfig.")
        logging.basicConfig(level=default_level)