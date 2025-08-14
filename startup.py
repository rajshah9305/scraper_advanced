#!/usr/bin/env python3
"""
Production startup script for Elite Web Scraper
Handles both development and production environments
"""

import os
import sys
import logging
from flask_scraper_app import app, socketio

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Elite Web Scraper on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Python version: {sys.version}")
    
    try:
        # Try to use socketio.run first (preferred for WebSocket support)
        socketio.run(
            app, 
            host=host, 
            port=port, 
            debug=debug,
            allow_unsafe_werkzeug=True,
            use_reloader=False
        )
    except Exception as e:
        logger.warning(f"SocketIO server failed to start: {e}")
        logger.info("Falling back to standard Flask server...")
        
        # Fallback to standard Flask server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False
        )

if __name__ == '__main__':
    main()
