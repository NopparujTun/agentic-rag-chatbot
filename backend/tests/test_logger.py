from app.core.logger import setup_logger
import logging

def test_setup_logger():
    setup_logger()
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0
    
    # Check if uvicorn loggers are properly configured
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(logger_name)
        assert len(logger.handlers) > 0
        assert not logger.propagate
