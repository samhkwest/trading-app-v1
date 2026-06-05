import os
from datetime import datetime

def should_ignore_dir(dirname):
    """
    Return True if directory should be ignored.
    """
    if dirname.startswith("__"):
        return True
    if dirname in {"data", "tool", "command"}:
        return True
    return False


def collect_py_files_to_single_text():
    root_folder = os.getcwd()

    # Script A's own absolute path (to ignore itself)
    self_path = os.path.abspath(__file__)

    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"file_list.txt"
    output_path = os.path.join(root_folder, output_filename)

    with open(output_path, "w", encoding="utf-8") as outfile:

        for root, dirs, files in os.walk(root_folder):

            # Filter ignored directories
            dirs[:] = [d for d in dirs if not should_ignore_dir(d)]

            for file in files:

                # ✅ Only .py files
                if not file.endswith(".py"):
                    continue

                file_path = os.path.abspath(os.path.join(root, file))

                # ✅ Ignore itself
                if file_path == self_path:
                    continue

                try:
                    outfile.write("=" * 80 + "\n")
                    outfile.write(f"FILE: {file_path}\n")
                    outfile.write("=" * 80 + "\n\n")

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                        outfile.write(infile.read())

                    outfile.write("\n\n\n")

                except Exception as e:
                    outfile.write(f"[Error reading file: {file_path}]\n")
                    outfile.write(f"{e}\n\n")

    print(f"\nDone. Output file created:\n{output_path}")


if __name__ == "__main__":
    collect_py_files_to_single_text()