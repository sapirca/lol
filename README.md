# LLM Backend Integration Project

This project integrates multiple LLM backends including OpenAI's GPT, Anthropic's Claude, Google's Gemini, and DeepSeek. The project allows you to interact with these backends through a console application and includes a React-based frontend (`react-lol`) for user interaction.

---

## Prerequisites

1. **Python**:
   - Ensure Python 3.9 or higher is installed on your system.
   - Install [MiniConda](https://docs.anaconda.com/miniconda/install/) for managing environments.

2. **VSCode**:
   - Install [Visual Studio Code](https://code.visualstudio.com/).
   - Search for **Python** in the extensions marketplace and click **Install**.

3. **Node.js and npm**:
   - Download and install [Node.js](https://nodejs.org/en/download/).
   - Verify installation:
     ```bash
     node --version
     npm --version
     ```

---

## Backend Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sapirca/lol.git
   cd lol
   ```

2. **Create a Conda Environment**:
   ```bash
   conda create --name lol_agent python=3.9
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

---

## Frontend Setup (`react-lol`)

1. **Navigate to the React Project**:
   ```bash
   cd ui/react-lol
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Set the Port**:
   - Open the `.env` file in the `react-lol` directory and set the desired port:
     ```properties
     PORT=1101
     ```

4. **Run the React Application**:
   ```bash
   npm start
   ```

5. **Access the Application**:
   - Open your browser and navigate to:
     ```
     http://localhost:1101
     ```

---

## Debugging the React Application in VSCode

1. **Open VSCode**:
   - Navigate to the `react-lol` directory in VSCode.

2. **Configure Debugging**:
   - Ensure the `.vscode/launch.json` file is configured as follows:
     ```jsonc
     {
         "type": "chrome",
         "request": "launch",
         "name": "Launch Chrome against localhost",
         "url": "http://localhost:1101",
         "webRoot": "${workspaceFolder}",
         "sourceMaps": false,
         "args": []
     }
     ```

3. **Start Debugging**:
   - Open the Debug panel in VSCode (Ctrl+Shift+D or Command+Shift+D).
   - Select **Launch Chrome against localhost**.
   - Click the green **Run** button to start debugging.

---

## Running the Backend and Frontend Together

1. **Start the Backend**:
   - Run the backend application:
     ```bash
     python -m console
     ```

2. **Start the Frontend**:
   - Navigate to the `react-lol` directory and start the React application:
     ```bash
     npm start
     ```

3. **Interact with the System**:
   - Open your browser and navigate to:
     ```
     http://localhost:1101
     ```

---

## Troubleshooting

1. **Port Already in Use**:
   - If the port `1101` is already in use, change it in the `.env` file:
     ```properties
     PORT=3001
     ```

2. **React Application Not Loading**:
   - Ensure all dependencies are installed:
     ```bash
     npm install
     ```

3. **Debugging Issues**:
   - Ensure the Chrome Debugger extension in VSCode is installed and up to date.

4. **Backend Errors**:
   - Check the logs in the terminal for any errors.
   - Ensure the `lol_secrets.py` file is correctly configured with valid API keys.

---

## Additional Notes

- To create a new React app, use:
  ```bash
  npx create-react-app my-app
  ```
- If you previously installed `create-react-app` globally, uninstall it:
  ```bash
  npm uninstall -g create-react-app
  ```

Let me know if you encounter any issues!