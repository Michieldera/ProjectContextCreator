import os
import argparse
import fnmatch
import webbrowser
import sys
import subprocess
import pyperclip

# --- Configuration ---
# Files to include
INCLUDED_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.html', '.css', '.json', '.md', 
    '.sql', '.go', '.rs', '.java', '.cpp', '.c', '.h', '.hpp', '.ino',
    '.txt', '.yaml', '.yml', '.toml', '.xml', '.sh', '.bat', '.env'
}

# Directories/Files to ignore
DEFAULT_IGNORE_DIRS = {
    '.git', 'node_modules', 'venv', '.venv', 'pycache', '__pycache__', 
    'dist', 'build', '.idea', '.vscode', '.gemini',
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'bun.lockb', 
    'images', 'assets', 'public', 'test-results', 'playwright-report',
    'coverage', '.next', '.nuxt', 'target',
    'logs.txt', '*.log', '*.audit.json'
}

GEMINI_URL = "https://gemini.google.com/app"
OUTPUT_FILENAME = "codebase_context.md"

# This is the prompt the user will paste into Gemini
USER_PROMPT = """I have attached a file `codebase_context.md` which contains the full source code and directory structure of my project. 

**Instruction:**
1.  **Analyze** the provided codebase to understand its architecture, tech stack, and key components.
2.  **Act** as a Senior Software Architect and Coding Assistant for this specific project.
3.  **Wait** for my next command. I will ask you to implement features, fix bugs, or explain code. When I do, provide concrete code examples and file modifications that fit the existing style and structure.

Please confirm you have ingested the context and are ready."""

META_PROMPT = """# Codebase Context
I am providing my codebase context below in this flattened markdown file. 

## Project Structure
(See file paths below)

---
"""

def load_gitignore(root_path):
    """
    Reads the .gitignore file from the root path and returns a list of patterns.
    """
    gitignore_path = os.path.join(root_path, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Could not read .gitignore: {e}")
    return patterns

def is_ignored(path, root_path, gitignore_patterns):
    """
    Checks if a file or directory should be ignored.
    """
    name = os.path.basename(path)
    
    # 1. Check default ignores (Exact match for dirs/files)
    if name in DEFAULT_IGNORE_DIRS:
        return True

    # 2. Check wildcards for defaults (like *.log)
    for pattern in DEFAULT_IGNORE_DIRS:
        if '*' in pattern:
            if fnmatch.fnmatch(name, pattern):
                return True

    # 3. Check gitignore patterns
    rel_path = os.path.relpath(path, root_path)
    # Normalize path separators for fnmatch
    rel_path = rel_path.replace(os.sep, '/')
    
    for pattern in gitignore_patterns:
        # Handle directory matches specifically if pattern ends with /
        if pattern.endswith('/') and os.path.isdir(path):
            if fnmatch.fnmatch(rel_path + '/', pattern) or fnmatch.fnmatch(name + '/', pattern):
                 return True
        
        # Standard match
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
            return True
            
    return False

def scan_and_pack(root_path, output_file):
    """
    Scans the directory and writes content to the output file.
    """
    print(f"Scanning project at: {root_path}...")
    
    gitignore_patterns = load_gitignore(root_path)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(META_PROMPT)
        
        file_count = 0
        total_size = 0
        
        # Walk the directory
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Modify dirnames in-place to skip ignored directories
            for d in list(dirnames):
                full_dir_path = os.path.join(dirpath, d)
                if is_ignored(full_dir_path, root_path, gitignore_patterns):
                    dirnames.remove(d)
            
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_path)
                
                # Check exclusions (skip the output file itself too)
                if filename == OUTPUT_FILENAME:
                    continue

                if is_ignored(file_path, root_path, gitignore_patterns):
                    continue
                    
                # Check extension
                _, ext = os.path.splitext(filename)
                if ext.lower() not in INCLUDED_EXTENSIONS:
                    continue
                
                # Read and Write
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Write to the single markdown file
                    # Using Markdown code blocks for separation
                    outfile.write(f"\n## File: `{rel_path}`\n\n```\n{content}\n```\n")
                    
                    file_count += 1
                    total_size += len(content)
                    print(f"  Packed: {rel_path}")
                    
                except Exception as e:
                    print(f"  Skipped (Read Error): {rel_path} - {e}")

    return file_count, total_size

def open_file_explorer(path):
    """
    Opens the file explorer at the given path.
    """
    try:
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    except Exception as e:
        print(f"Could not open file explorer: {e}")

def main():
    parser = argparse.ArgumentParser(description="Pack codebase context for Gemini (File Upload).")
    parser.add_argument('path', nargs='?', help="Path to the project root directory")
    parser.add_argument('--path', '-p', dest='flag_path', help="Path to the project root directory (alternative flag)")
    
    args = parser.parse_args()
    
    # Determine root path
    CONTEXT_ROOT = os.environ.get('CONTEXT_ROOT')
    target_path = args.path or args.flag_path or CONTEXT_ROOT or os.getcwd()
    target_path = os.path.abspath(target_path)

    if not os.path.isdir(target_path):
        print(f"Error: The path '{target_path}' is not a valid directory.")
        return
    
    output_path = os.path.join(os.getcwd(), OUTPUT_FILENAME)

    try:
        file_count, total_chars = scan_and_pack(target_path, output_path)
        
        if file_count == 0:
            print("No matching files found to pack.")
            return

        # Prepare Prompt
        try:
            pyperclip.copy(USER_PROMPT)
            prompt_status = "Copied to clipboard!"
        except Exception:
            prompt_status = "Could not copy to clipboard (missing dependency?)"
        
        # Also write prompt to file just in case
        with open("prompt.txt", "w", encoding="utf-8") as f:
            f.write(USER_PROMPT)

        print("-" * 50)
        print(f"SUCCESS! Context packed into: {OUTPUT_FILENAME}")
        print(f" - Files included: {file_count}")
        print(f" - Approximate size: {total_chars / 1024 / 1024:.2f} MB")
        print("-" * 50)
        print(f"INSTRUCTION PROMPT: {prompt_status}")
        print("-" * 50)
        print("STEPS:")
        print("1. Gemini Web App is opening...")
        print("2. DRAG & DROP 'codebase_context.md' into the chat.")
        print("3. PASTE (Ctrl+V) the instruction prompt.")
        print("-" * 50)
        
        # Open Browser
        webbrowser.open(GEMINI_URL)
        
        # Open Explorer
        if sys.platform == 'win32':
            subprocess.Popen(f'explorer /select,"{output_path}"')
        else:
            open_file_explorer(os.path.dirname(output_path))

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
