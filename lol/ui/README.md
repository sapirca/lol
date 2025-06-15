# Web Chat UI

This directory contains a simple web-based chat interface.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Setup and Running

1.  **Navigate to the `lol/ui` directory:**
    ```bash
    cd path/to/your/project/lol/ui
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies:**
    The only external dependency for this basic UI is Flask.
    ```bash
    pip install Flask
    ```

5.  **Run the Flask application:**
    ```bash
    python app.py
    ```

6.  **Open the web UI:**
    Open your web browser and go to `http://127.0.0.1:5000/` or `http://localhost:5000/`. If you are running this on a different machine or a VM, you might need to access it via the machine's IP address on port 5000 (e.g., `http://<your-machine-ip>:5000/`), as the Flask app is configured to run on `0.0.0.0`.

## Project Structure

-   `app.py`: The Flask backend application.
-   `templates/`: Contains HTML templates.
    -   `index.html`: The main chat interface page.
-   `static/`: Contains static files.
    -   `style.css`: CSS for styling the chat interface.
    -   `chat.js`: JavaScript for frontend chat logic.
-   `README.md`: This file.
