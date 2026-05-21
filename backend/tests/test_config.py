import pytest
from app.core.config import load_config
import os
import yaml

def test_load_config_success(tmp_path):
    config_data = {"app": {"name": "test_app"}}
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    
    config = load_config(str(config_file))
    assert config == config_data

def test_load_config_error():
    with pytest.raises(RuntimeError):
        load_config("non_existent_file.yaml")
