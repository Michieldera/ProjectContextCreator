# Prime Context Creator

**Prime** is a powerful Python utility designed to bridge the gap between your local codebase and Large Language Models (LLMs) like Google Gemini. 

It solves the "context window" and "clipboard limit" problems by smartly packing your entire relevant codebase into a single, optimized Markdown file (`codebase_context.md`) and automatically preparing a role-specific prompt for your LLM.

## Features

- 🚀 **One-Step Workflow**: Scans, packs, and opens everything you need in seconds.
- 📂 **Smart Code Packing**: Recursively finds code files while respecting `.gitignore` and skipping irrelevant directories (like `node_modules`, `venv`, `build`).
- 🤖 **Auto-Prompting**: Automatically copies a "Senior Architect" system prompt to your clipboard, ready for pasting.
- 🛡️ **Privacy Focused**: Everything runs locally. No code is sent to any API by the script itself—you control the upload.
- ⚡ **Zero Config**: Works out of the box, but fully customizable.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YourUsername/prime-context-creator.git
    cd prime-context-creator
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Optional) Set up Environment**:
    You can create a `.env` file if you want to extend functionality later, but the core file-upload workflow requires no API keys.

## Usage

Run the script pointing to your project directory:

```bash
python prime.py -p /path/to/your/project
```

### What happens next?
1.  **Scanning**: The script scans your project, ignoring binary files and heavy folders.
2.  **Packing**: It creates a `codebase_context.md` file in the current directory.
3.  **Launching**: It opens the Gemini Web App (https://gemini.google.com/app) and your local file explorer.
4.  **Prompting**: A professional instruction prompt is copied to your clipboard.

### Your Step-by-Step in the Browser:
1.  **Drag & Drop** the `codebase_context.md` file into the Gemini chat window.
2.  **Paste** (Ctrl+V) the prompt into the message box.
3.  Start coding with an AI that knows your entire project!

## Customization

You can modify `prime.py` to change:
- `INCLUDED_EXTENSIONS`: Add or remove file types to scan.
- `DEFAULT_IGNORE_DIRS`: Add directories to always skip.

## License

MIT
