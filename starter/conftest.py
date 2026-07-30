import pytest
import sys
import os

# Add the current directory to path so we can import app and sudoku_logic
sys.path.insert(0, os.path.dirname(__file__))

import app as app_module
import sudoku_logic


@pytest.fixture
def app():
    """Create and configure a test Flask app instance."""
    app_instance = app_module.app
    app_instance.config['TESTING'] = True
    
    # Reset CURRENT state before each test
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    
    return app_instance


@pytest.fixture
def client(app):
    """Provide a Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Provide a Flask CLI runner for testing CLI commands."""
    return app.test_cli_runner()
