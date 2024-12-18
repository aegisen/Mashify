# Import the Flask app instance from the src.app module
from src.app import app

if __name__ == "__main__":

    # Run the Flask application with debugging enabled.
    # The `use_reloader=True` ensures the server restarts on code changes,
    # and `use_debugger=True` provides an interactive debugger in case of errors.
    app.run(debug=True, use_reloader=True, use_debugger=True)