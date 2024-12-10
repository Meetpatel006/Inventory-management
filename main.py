"""
Main entry point for the Inventory Management System.
"""
import logging
from src.core.setup import setup_logging, initialize_directories
from src.gui.login_window import LoginWindow

def main():
    # Initialize directories
    initialize_directories()
    
    # Setup logging
    setup_logging()
    
    try:
        # Initialize login window
        root = LoginWindow()
        root.window.mainloop()
    except Exception as e:
        logging.error(f"Application failed to start: {str(e)}")
        raise

if __name__ == "__main__":
    main()
