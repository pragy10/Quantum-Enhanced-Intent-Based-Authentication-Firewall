import os
from pathlib import Path

def collect_codes(root_folder="."):
    output_file = "collected_codes.txt"

    code_extensions = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r',
        '.sql', '.html', '.css', '.scss', '.sass', '.vue', '.sh', '.bash',
        '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.sol'
    }

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(root_folder):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env', 'build', 'dist', 'results', 'myenv']]

            for file in sorted(files):
                file_path = Path(root) / file

                if file == output_file or file == 'collect_codes.py':
                    continue

                if file_path.suffix.lower() in code_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()

                        relative_path = file_path.relative_to(root_folder)
                        outfile.write(f"{'='*80}\n")
                        outfile.write(f"File: {relative_path}\n")
                        outfile.write(f"{'='*80}\n\n")
                        outfile.write(content)
                        outfile.write(f"\n\n")

                    except Exception as e:
                        outfile.write(f"{'='*80}\n")
                        outfile.write(f"File: {file_path.relative_to(root_folder)}\n")
                        outfile.write(f"{'='*80}\n")
                        outfile.write(f"Error reading file: {str(e)}\n\n")

    print(f"Code collection complete. Output saved to {output_file}")

if __name__ == "__main__":
    collect_codes()