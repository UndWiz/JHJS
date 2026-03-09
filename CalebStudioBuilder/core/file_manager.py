"""
FILE MANAGER
============

This module safely handles all file and directory creation for
CalebStudioBuilder.

It prevents:

- overwriting existing files
- broken directory paths
- unsafe writes
- missing folders

All builder systems must use this module when creating files.
"""

import os
import datetime


class FileManager:

    def __init__(self, base_path="studio"):
        """
        Initialize the file manager.
        """
        self.base_path = base_path

        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def create_directory(self, path):
        """
        Create a directory safely.
        """
        full_path = os.path.join(self.base_path, path)

        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"[FileManager] Created directory: {full_path}")
        else:
            print(f"[FileManager] Directory already exists: {full_path}")

    def write_file(self, path, content):
        """
        Write a file safely without overwriting existing files.
        """

        full_path = os.path.join(self.base_path, path)

        directory = os.path.dirname(full_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(full_path):
            print(f"[FileManager] File already exists, skipping: {full_path}")
            return False

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[FileManager] Created file: {full_path}")
        return True

    def append_file(self, path, content):
        """
        Append data to a file.
        """

        full_path = os.path.join(self.base_path, path)

        directory = os.path.dirname(full_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(full_path, "a", encoding="utf-8") as f:
            f.write(content)

        print(f"[FileManager] Appended to file: {full_path}")

    def file_exists(self, path):
        """
        Check if a file exists.
        """
        full_path = os.path.join(self.base_path, path)
        return os.path.exists(full_path)

    def list_files(self, path=""):
        """
        List files in a directory.
        """
        full_path = os.path.join(self.base_path, path)

        if not os.path.exists(full_path):
            return []

        return os.listdir(full_path)

    def timestamp(self):
        """
        Return current timestamp string.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
