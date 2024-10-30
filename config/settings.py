from pathlib import Path
from datetime import datetime

class Settings:
    DEFAULT_OUTPUT_DIR = Path("output")
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    
    @classmethod
    def get_timestamp(cls) -> str:
        return datetime.now().strftime(cls.TIMESTAMP_FORMAT)
    
    @classmethod
    def get_clone_dir(cls, timestamp: str) -> Path:
        return cls.DEFAULT_OUTPUT_DIR / f"repo_clone_{timestamp}"
    
    @classmethod
    def get_output_file(cls, timestamp: str) -> Path:
        return cls.DEFAULT_OUTPUT_DIR / f"scan_result_{timestamp}.txt"
