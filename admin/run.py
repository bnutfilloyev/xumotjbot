"""
Enhanced server runner with error handling for the XumotjBot Admin Panel.
"""
import logging
import os
import sys
import traceback
import uvicorn
from admin import app, logger
from config import HOST, PORT

def configure_logging():
    """Configure more detailed logging for troubleshooting."""
    # Configure root logger to show all messages
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Add stream handler if not already present
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        root_logger.addHandler(handler)
    
    # Enable more verbose logging for relevant modules
    logging.getLogger('starlette').setLevel(logging.DEBUG)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('starlette_admin').setLevel(logging.DEBUG)

def run_server():
    """Start the admin server with enhanced error handling."""
    try:
        # Configure detailed logging
        configure_logging()
        
        # Log server information
        logger.info(f"Starting admin server at http://{HOST}:{PORT}/admin")
        logger.info(f"Static files directory: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')}")
        
        # Run the server with reload enabled for development
        uvicorn.run(
            "admin:app", 
            host=HOST, 
            port=PORT, 
            reload=True,  # Enable hot reloading
            log_level="debug"
        )
    except Exception as e:
        logger.critical(f"Server failed to start: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_server()
