"""
Main Application Script

This script creates and runs the Flask web application using the 'create_app' function from the 'website' module.

Modules:
    - website: Module containing the Flask application factory and related components.
    - create_app: Function to create and configure the Flask application.
    - app: Flask application instance.

Usage:
    Run this script to start the Flask web server.

Note:
    Debug mode is enabled for development. Disable it for production by setting `debug=False`.
"""

from website import create_app

app = create_app()

# Runs the web server only if the main script is executed (not when imported elsewhere)
if __name__ == '__main__':
    app.run(debug=True, port=3000)  # Disable debug mode for production
