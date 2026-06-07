import os

def should_ignore(path, name):
    """
    Returns True if the file or directory should be ignored.
    """
    # Ignore files starting with "__"
    if os.path.isfile(path) and name.startswith("__"):
        return True

    # Ignore directories starting with "__"
    if os.path.isdir(path):
        if name.startswith("__"):
            return True
        if name.lower() == "backup":
            return True

    return False


def print_tree(start_path, prefix=""):
    """
    Recursively prints the directory tree structure,
    ignoring specific files and directories.
    """
    try:
        items = sorted(os.listdir(start_path))
    except PermissionError:
        print(prefix + "└── [Permission Denied]")
        return

    # Filter items
    filtered_items = []
    for item in items:
        full_path = os.path.join(start_path, item)
        if should_ignore(full_path, item):
            continue
        filtered_items.append(item)

    total_items = len(filtered_items)

    for index, item in enumerate(filtered_items):
        path = os.path.join(start_path, item)
        is_last = index == total_items - 1

        connector = "└── " if is_last else "├── "
        print(prefix + connector + item)

        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension)


if __name__ == "__main__":
    # Directory where this script is located (Directory A)
    base_directory = os.path.dirname(os.path.abspath(__file__))

    print(f"Directory tree for: {base_directory}\n")
    print_tree(base_directory)