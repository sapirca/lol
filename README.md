# LLM Backend Integration Project

This project integrates multiple LLM backends including OpenAI's GPT, Anthropic's Claude, Google's Gemini, and DeepSeek. The project allows you to interact with these backends through a console application.

## Prerequisites

1. **Python**:
   - Ensure Python 3.9 or higher is installed on your system.
   - Install [Anaconda](https://www.anaconda.com/products/distribution) for managing environments.

2. **VSCode**:
   - Install [Visual Studio Code](https://code.visualstudio.com/).
   - Search for **Python** in the extensions marketplace and click **Install**.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/llm-backend-integration.git
   cd llm-backend-integration
   ```

2. **Create a Conda Environment**:
   ```bash
   conda create --name lol_agent python=3.8
   conda activate lol_agent
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**:
   - Create a `secrets.py` file in the root directory and add your API keys:
     ```python
     OPENAI_API_KEY = 'your-openai-api-key'
     CLAUDE_API_KEY = 'your-claude-api-key'
     GEMINI_API_KEY = 'your-gemini-api-key'
     DEEPSEEK_API_KEY = 'your-deepseek-api-key'
     ```

## Using VSCode

1. **Select the Python Interpreter**:
   - Open the Command Palette (Command+Shift+P on macOS or Ctrl+Shift+P on Windows/Linux).
   - Type and select **Python: Select Interpreter**.
   - Choose the Conda environment `lol_agent` created earlier.

2. **Run the Program**:
   - Open `console.py` in VSCode.
   - Click the **Run and Debug** icon on the left sidebar (Ctrl+Shift+D).
   - Click the green **Run** button at the top to execute the program.

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

4. **DeepSeek**:
   - Visit the DeepSeek API documentation or your API provider to request access.
   - Add the API key to `secrets.py` under `DEEPSEEK_API_KEY`.

## Running the Project

### Using the Console

1. **Run the Console Application**:
   ```bash
   python -m console
   ```

2. **Interact with the AI**:
   - Type your input when prompted (`You:`).
