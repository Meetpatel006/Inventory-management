"""System setup and initialization functions"""
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Configure logging system with both file and console handlers"""
    try:
        # Create logs directory
        log_dir = Path.cwd() / "ims-info" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        log_file = log_dir / f"ims_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logging.info("Logging system initialized")
        return True
    except Exception as e:
        print(f"Failed to setup logging: {str(e)}")
        return False

def initialize_directories():
    """Initialize required directory structure"""
    try:
        base_dir = Path.cwd() / "ims-info"  # Use current working directory
        dirs = {
            'base': base_dir,
            'bills': base_dir / "bills",
            'logs': base_dir / "logs",
            'csv': base_dir / "bills" / "csv",  # Ensure 'csv' directory is included
            'cache': base_dir / "cache"
        }
        
        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            
        return dirs
    except Exception as e:
        logging.error(f"Error initializing directories: {str(e)}")
        return None