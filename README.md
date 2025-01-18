# README: AI Agent with Multiple LLM Backends

## Overview

This project implements an AI agent that communicates with users using multiple LLM backends (e.g., GPT, Claude, Gemini). It integrates tools for configuration, dynamic prompts, and house setup using XML.

---

## Setting up the Project

### Prerequisites
1. Install [Conda](https://docs.conda.io/en/latest/miniconda.html).
2. Ensure you have **Python 3.8+** installed.
3. Install **Visual Studio Code** (recommended) and the Python extension.

---

### Steps to Set Up the Virtual Environment

1. **Create a Conda Environment**:
   ```bash
   conda create --name lol_agent python=3.8 -y
   ```

2. **Activate the Environment**:
   ```bash
   conda activate lol_agent
   ```

3. **Install Required Libraries**:
   ```bash
   pip install openai requests
   ```

4. **Download or Clone the Repository**:
   Navigate to your desired directory and run:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

5. **Set Up API Keys**:
   - Create a file named `secrets.py` in the project root.
   - Add the following lines to `secrets.py`:
     ```python
     OPENAI_API_KEY = "your_openai_api_key"
     CLAUDE_API_KEY = "your_claude_api_key"
     GEMINI_API_KEY = "your_gemini_api_key"
     ```
   - Replace the placeholder values with your actual API keys.

6. **Verify the House Configuration XML**:
   - Ensure the `house_config.xml` file is present in the project root directory and properly formatted.

---

## Setting Up the Project in VSCode

1. **Open the Project in VSCode**:
   - Launch **Visual Studio Code**.
   - Click on **File > Open Folder** and select the project folder (e.g., `lol`).

2. **Install the Python Extension**:
   - Go to the Extensions Marketplace (Ctrl+Shift+X).
   - Search for **Python** and click **Install**.

3. **Select the Python Interpreter**:
   - Open the Command Palette (Ctrl+Shift+P).
   - Type and select **Python: Select Interpreter**.
   - Choose the Conda environment `lol_agent` created earlier.

4. **Run the Program**:
   - Open `console.py` in VSCode.
   - Click the **Run and Debug** icon on the left sidebar (Ctrl+Shift+D).
   - Click the green **Run** button at the top to execute the program.

---

## Obtaining API Keys for Backends

1. **OpenAI (GPT)**:
   - Visit [OpenAI API Keys](https://platform.openai.com/signup/).
   - Create an account and generate an API key.
   - Add it to `secrets.py` under `OPENAI_API_KEY`.

2. **Claude**:
   - Visit the Anthropic API documentation or your API provider to request access to Claude.
   - Add the API key to `secrets.py` under `CLAUDE_API_KEY`.

3. **Gemini**:
   - Contact your Gemini API provider or support team to request API access.
   - Add the API key to `secrets.py` under `GEMINI_API_KEY`.

---

## Running the Project

### Using the Console
1. **Run the Console Application**:
   ```bash
   python -m console
   ```

2. **Interact with the AI**:
   - Type your input when prompted (`You:`).
   - To exit the session, type `exit`.

3. **Log Files**:
   - Each session creates a log file named `conversation_log_<date>_<time>.txt` in the project directory.
   - Logs include timestamps, user inputs, and AI responses.

### Running Tests
1. **Run the Test File**:
   ```bash
   python -m unittest test_main_controller.py
   ```

2. **Expected Behavior**:
   - The test file ensures the `communicate` method in `MainController` works as expected, including proper handling of chat history and backend interactions.

---

## Key Files and Structure

1. **`backends.py`**:
   - Defines the backends (e.g., GPT, Claude, Gemini) and includes API integration.
   - Supports stubbed responses for testing without live APIs.

2. **`config.py`**:
   - Contains configurations such as:
     - Selected backend (`selected_backend`).
     - Stub usage (`use_stub`).

3. **`prompts.py`**:
   - Stores the main prompt and sub-prompts.
   - Concatenates the prompts dynamically with the house configuration.

4. **`main_controller.py`**:
   - Orchestrates the interaction between user input, prompts, and backends.
   - Loads the house configuration from `house_config.xml`.

5. **`console.py`**:
   - Provides a CLI interface for user interaction.
   - Logs user input and AI responses to timestamped log files.

6. **`house_config.xml`**:
   - Describes the house elements (e.g., doors, windows) used in the prompt.
   - Example:
     ```xml
     <house>
         <main_door>
             <type>Wooden</type>
             <color>Brown</color>
             <locked>true</locked>
         </main_door>
         <garage_door>
             <type>Automatic</type>
             <color>White</color>
             <locked>false</locked>
         </garage_door>
         <windows>
             <window id="1">
                 <type>Sliding</type>
                 <open>true</open>
             </window>
             <window id="2">
                 <type>Casement</type>
                 <open>false</open>
             </window>
         </windows>
     </house>
     ```

7. **`secrets.py`**:
   - Stores the API keys for the backends in a secure and centralized location.

---