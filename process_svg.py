#!/usr/bin/env python3
import os
import sys
import re

def sanitize_filename(filepath):
    """
    Remove path, then remove extension,
    then keep only letters, numbers, underscores, and dashes.
    """
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    sanitized = re.sub(r'[^A-Za-z0-9_-]', '', base_name)
    return sanitized

def process_svg_file(svg_path):
    print(f"Processing file: {svg_path}")
    
    # Sanitize filename for replacement
    sanitized_name = sanitize_filename(svg_path)
    print(f"Sanitized filename: {sanitized_name}")
    
    # Read the file content
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Count occurrences
    raw_cls_count = content.count("cls")
    replaced_cls_count = content.count(f"{sanitized_name}-cls")
    
    print(f"Found {raw_cls_count} occurrences of 'cls'.")
    print(f"Found {replaced_cls_count} occurrences of '{sanitized_name}-cls'.")
    
    # If the counts are the same (and not zero), we assume it's already replaced
    if raw_cls_count == replaced_cls_count and raw_cls_count != 0:
        print("Skipping file because it appears to already be updated.")
        return
    
    # Otherwise, do the replacement
    replaced_content = content.replace("cls", f"{sanitized_name}-cls")
    
    # Overwrite the file with the replaced content
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(replaced_content)
    
    print(f"Finished updating {svg_path}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python replace_cls.py <file_or_directory>")
        sys.exit(1)
    
    path = sys.argv[1]

    # Check if path is a directory or a file
    if os.path.isdir(path):
        print(f"Detected directory: {path}")
        for filename in os.listdir(path):
            if filename.lower().endswith(".svg"):
                full_path = os.path.join(path, filename)
                process_svg_file(full_path)
    else:
        if os.path.isfile(path):
            if path.lower().endswith(".svg"):
                process_svg_file(path)
            else:
                print(f"Provided file is not an .svg: {path}")
        else:
            print(f"Provided path is not a file or directory: {path}")

if __name__ == "__main__":
    main()