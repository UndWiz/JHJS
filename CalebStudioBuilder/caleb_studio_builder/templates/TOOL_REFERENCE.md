# CALEB MASTER TOOL SCHEMA REFERENCE
Use these exact XML tags to interact with the local environment:

1.  **Folder Creation:** `<create_folder>path/to/dir</create_folder>`
2.  **File Writing:** `<write_file path="file.py">content</write_file>`
3.  **Section Patching:** `<patch_file path="file.py" line_start="10" line_end="20">new_content</patch_file>`
4.  **Terminal Execution:** `<run_command>pip install requests</run_command>`
5.  **File Deletion:** `<delete_file>path/to/file</delete_file>`
6.  **Code Inspection:** `<read_file>path/to/file</read_file>`
7.  **Directory Mapping:** `<list_dir>path/to/dir</list_dir>`
8.  **Grep Search:** `<search_codebase pattern="class Name">project_root</search_codebase>`
9.  **File Appending:** `<append_file path="log.txt">new_line</append_file>`
10. **User Clarification:** `<ask_user>Am I authorized to delete this?</ask_user>`
