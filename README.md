Sakila Code Analyzer (LLM-Powered, Offline)

==================================================

Overview:
---------
This tool analyzes a Java/Python/JavaScript codebase (like SakilaProject) using a local LLM (e.g., Mistral via Ollama) to extract useful insights:
- Code overviews
- Function/method signatures
- Return types
- Patterns or complexity
The output is saved as a structured JSON file for each file processed.

Features:
---------
- Uses open-source LLMs (Mistral/Mixtral) locally via Ollama
- Incremental per-file analysis with intermediate JSON output
- Splits long files into chunks automatically
- Graceful error handling for LLM or JSON failures

Setup Instructions:
-------------------
1. Clone the repo and navigate to the folder:
   git clone https://github.com/jagadish2621/code_analyzer.git

2. Create and activate a virtual environment:
   python -m venv venv
   venv\Scripts\activate (Windows) OR source venv/bin/activate (Linux/macOS)

3. Install dependencies:
   pip install -r requirements.txt

4. Run the model locally:
   ollama run mistral  # or mixtral

5. Run the analyzer:
   python app.py

Output:
-------
A JSON file named `result.json` will be created in the root directory.
Example structure:
{
  "files": [
    {
      "filename": "src/example/MockTests.java",
      "functions": [
        {
          "overview": "This file contains unit tests...",
          "methods": [
            {
              "name": "testInsertMovie",
              "parameters": [],
              "returns": "void"
            }
          ],
          "patterns": ["JUnit test pattern"]
        }
      ]
    }
  ]
}

Issues Faced & Fixes:
---------------------
1. ModuleNotFoundError: langchain_community
   → Installed missing dependency via pip and corrected imports.

2. JSONDecodeError due to malformed LLM response
   → Cleaned invalid characters before parsing using regex.

3. LLM response too slow for full project
   → Implemented per-file intermediate output saving to improve UX.

4. argparse error with unnamed argument
   → Removed buggy CLI parsing and used static path-based invocation.

5. Deprecated LangChain call method
   → Switched to `llm.invoke()` instead of deprecated `llm([msg])`.

Future Improvements:
--------------------
- Multi-threaded file processing
- CLI argument for project path and model name
- Add support for more languages like C++, PHP
- Visualization/dashboard for JSON output

Credits:
--------
- LangChain
- Ollama
- Mistral/Mixtral open-source LLMs

Author:
-------
Jagadeesan

