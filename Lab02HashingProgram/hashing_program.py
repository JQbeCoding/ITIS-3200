import os
import sys
import json
import hashlib

def hash_file(filepath):
    """Calculates the SHA-256 cryptographic hash of a file's contents."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def traverse_directory(directory_path):
    """Navigates the directory and calls hash_file for each file. Returns a dict of filepath -> hash."""
    file_hashes = {}
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            filepath = os.path.join(root, file)
            # Normalize path for cross-platform consistency
            filepath = os.path.normpath(filepath)
            file_hash = hash_file(filepath)
            if file_hash:
                file_hashes[filepath] = file_hash
    return file_hashes

def generate_table():
    """Prompts for a directory, hashes files, and saves to hashtable.json"""
    directory_path = input("Enter the directory path to hash: ").strip()
    if not os.path.isdir(directory_path):
        print("Invalid directory path.")
        return

    print(f"Hashing files in {directory_path}...")
    file_hashes = traverse_directory(directory_path)
    
    try:
        with open("hashtable.json", "w") as f:
            json.dump(file_hashes, f, indent=4)
        print("Hash table generated as hashtable.json")
    except Exception as e:
        print(f"Error saving hash table: {e}")

def validate_hash():
    """Reads hashtable.json, traverses directory, and verifies hashes."""
    if not os.path.exists("hashtable.json"):
        print("hashtable.json not found. Please generate a hash table first.")
        return
    
    try:
        with open("hashtable.json", "r") as f:
            stored_hashes = json.load(f)
    except Exception as e:
        print(f"Error reading hashtable.json: {e}")
        return
    
    directory_path = input("Enter the directory path to verify: ").strip()
    if not os.path.isdir(directory_path):
        print("Invalid directory path.")
        return

    print(f"Verifying files in {directory_path}...")
    current_hashes = traverse_directory(directory_path)
    
    stored_files = set(stored_hashes.keys())
    current_files = set(current_hashes.keys())
    
    deleted_files = stored_files - current_files
    new_files = current_files - stored_files
    common_files = stored_files.intersection(current_files)
    
    hash_table_updated = False
    
    # BONUS: Check for renamed files
    new_files_to_remove = []
    deleted_files_to_remove = []
    
    for new_file in new_files:
        new_hash = current_hashes[new_file]
        for deleted_file in deleted_files:
            if stored_hashes[deleted_file] == new_hash:
                print(f"File name change detected, {deleted_file} has been renamed to {new_file}")
                # Update hash table
                del stored_hashes[deleted_file]
                stored_hashes[new_file] = new_hash
                hash_table_updated = True
                
                new_files_to_remove.append(new_file)
                deleted_files_to_remove.append(deleted_file)
                break
                
    for f in new_files_to_remove:
        new_files.remove(f)
    for f in deleted_files_to_remove:
        deleted_files.remove(f)
        
    for deleted_file in deleted_files:
        print(f"File deleted: {deleted_file}")
        
    for new_file in new_files:
        print(f"New document found: {new_file}")
        
    for file in common_files:
        if stored_hashes[file] == current_hashes[file]:
            print(f"{file} hash is valid")
        else:
            print(f"{file} hash is invalid")
            
    if hash_table_updated:
        with open("hashtable.json", "w") as f:
            json.dump(stored_hashes, f, indent=4)
        print("Hash table updated due to file renames.")

def main():
    while True:
        print("\n--- Hashing Program ---")
        print("1. Generate a new hash table")
        print("2. Verify hashes")
        print("3. Exit")
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            generate_table()
        elif choice == '2':
            validate_hash()
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice, please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
