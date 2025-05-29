import os
import fnmatch

LICENSE_HEADER = {
    '.py': (
        "# Copyright 2025 Leon Hecht\n"
        "# Licensed under the Apache License, Version 2.0 (see LICENSE file)\n\n"
    ),
    '.js': (
        "/*\n"
        " * Copyright 2025 Leon Hecht\n"
        " * Licensed under the Apache License, Version 2.0 (see LICENSE file)\n"
        " */\n\n"
    ),
    '.jsx': (
        "/*\n"
        " * Copyright 2025 Leon Hecht\n"
        " * Licensed under the Apache License, Version 2.0 (see LICENSE file)\n"
        " */\n\n"
    ),
    '.ts': (
        "/*\n"
        " * Copyright 2025 Leon Hecht\n"
        " * Licensed under the Apache License, Version 2.0 (see LICENSE file)\n"
        " */\n\n"
    ),
    '.tsx': (
        "/*\n"
        " * Copyright 2025 Leon Hecht\n"
        " * Licensed under the Apache License, Version 2.0 (see LICENSE file)\n"
        " */\n\n"
    ),
    '.css': (
        "/*\n"
        " * Copyright 2025 Leon Hecht\n"
        " * Licensed under the Apache License, Version 2.0 (see LICENSE file)\n"
        " */\n\n"
    ),
}

FILE_EXTENSIONS = set(LICENSE_HEADER.keys())

def prepend_license_header(file_path, header):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "Copyright 2025 Leon Hecht" in content[:200]:
            # Already has the header
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(header + content)
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main(root_dir='.'):
    updated_files = []
    for dirpath, _, files in os.walk(root_dir):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in FILE_EXTENSIONS:
                full_path = os.path.join(dirpath, file)
                header = LICENSE_HEADER[ext]
                if prepend_license_header(full_path, header):
                    updated_files.append(full_path)
    print(f"Added license header to {len(updated_files)} files.")
    if updated_files:
        print("Updated files:")
        for path in updated_files:
            print(f" - {path}")

if __name__ == '__main__':
    # Set the directory where your source code lives
    # Use '.' for the current directory
    main('.')
