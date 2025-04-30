import os
import json
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import HumanMessage

CODE_EXTENSIONS = ['.py', '.java', '.js']
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200

SUMMARY_PROMPT = PromptTemplate(
    input_variables=["code"],
    template="""
You are an AI code analyzer. Analyze the following code and extract:
1. A brief overview of what it does.
2. Key functions/methods with their names, parameters, and return values.
3. Complexity or noteworthy patterns.
Return the result in JSON format.

CODE:
{code}
"""
)

llm = ChatOllama(model="mistral")

def get_code_files(base_path: str) -> List[Path]:
    """Return a list of all code files in the directory"""
    return [file for file in Path(base_path).rglob("*") if file.suffix in CODE_EXTENSIONS]

def split_code(code: str) -> List[str]:
    """Splits code into chunks for analysis"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(code)

def analyze_code_chunk(code_chunk: str) -> Dict:
    """Analyzes each chunk of code using the LLM"""
    try:
        message = HumanMessage(content=SUMMARY_PROMPT.format(code=code_chunk))
        response = llm.invoke([message])

        sanitized_response = sanitize_response(response.content)

        return json.loads(sanitized_response)
    except json.JSONDecodeError as je:
        print(f"JSON Decode Error: {je}")
        return {"error": "Invalid JSON from model", "raw_output": response.content}
    except Exception as e:
        print(f"Error analyzing code chunk: {e}")
        return {"error": str(e)}

def sanitize_response(response: str) -> str:
    """Sanitize the response to remove control characters or other invalid JSON elements"""
    response = re.sub(r'[\x00-\x1F\x7F]', '', response) 
    response = response.replace('\n', ' ').replace('\r', ' ')
    response = response.replace('“', '"').replace('”', '"')
    return response

def analyze_file(file: Path) -> Dict:
    """Analyzes an entire file by reading its content and splitting it into chunks"""
    print(f"Analyzing {file}...")
    file_summary = {"filename": str(file), "functions": []}
    try:
        content = file.read_text(encoding='utf-8')
        chunks = split_code(content)
        for chunk in chunks:
            analysis = analyze_code_chunk(chunk)
            if isinstance(analysis, dict):
                file_summary["functions"].append(analysis)
    except Exception as e:
        print(f"Failed to read {file}: {e}")
        file_summary["error"] = str(e)
    return file_summary

def main(project_path: str, output_json: str):
    """Main function that processes the project files in parallel and writes the results to JSON"""
    files = get_code_files(project_path)

    with open(output_json, 'w', encoding='utf-8') as f:
        f.write('{\n  "project_overview": [],\n  "files": [\n')

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(analyze_file, file): file for file in files}
        for i, future in enumerate(as_completed(futures)):
            result = future.result()

            with open(output_json, 'a', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                if i < len(files) - 1:
                    f.write(',\n')
                else:
                    f.write('\n')

    with open(output_json, 'a', encoding='utf-8') as f:
        f.write('  ]\n}\n')

    print(f"Analysis complete. Output saved to {output_json}")

if __name__ == "__main__":

    input_folder = "sakila_proj/SakilaProject"
    output_file = "output/result.json"
    
    main(input_folder, output_file)
