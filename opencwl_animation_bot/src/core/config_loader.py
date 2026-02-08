import os
import re
import yaml
import logging

logger = logging.getLogger(__name__)

def load_config(filepath: str) -> dict:
    """
    Load YAML config and expand environment variables.
    Format: ${VAR_NAME} or ${VAR_NAME:default_value}
    """
    pattern = re.compile(r'\$\{([^}^{]+)\}')

    def replace_env_var(match):
        env_var_str = match.group(1)
        if ':' in env_var_str:
            var_name, default_value = env_var_str.split(':', 1)
            return os.environ.get(var_name, default_value)
        return os.environ.get(env_var_str, '')

    with open(filepath, 'r') as f:
        content = f.read()

    # Expand environment variables
    expanded_content = pattern.sub(replace_env_var, content)

    try:
        config = yaml.safe_load(expanded_content)
        logger.info(f"Loaded configuration from {filepath}")
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise
