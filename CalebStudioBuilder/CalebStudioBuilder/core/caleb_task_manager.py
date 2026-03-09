"""
CALEB TASK MANAGER
==================
Orchestrates tasks for CalebStudioBuilder.
Handles AI engine setup, asset downloads, project scaffolding, and automation.
"""

import os
import subprocess
from queue import Queue
from threading import Thread
from memory_manager import MemoryManager

class TaskManager:

    def __init__(self, project_root="~/CalebStudioProjects"):
        self.project_root = os.path.expanduser(project_root)
        self.task_queue = Queue()
        self.memory = MemoryManager()
        self.completed_tasks = []

    # ------------------------------
    # 1. Add task to queue
    # ------------------------------
    def add_task(self, task_name, func, *args, **kwargs):
        task = {"name": task_name, "func": func, "args": args, "kwargs": kwargs}
        self.task_queue.put(task)
        print(f"[TASK ADDED] {task_name}")

    # ------------------------------
    # 2. Execute a single task
    # ------------------------------
    def execute_task(self, task):
        name = task["name"]
        try:
            print(f"[EXECUTING] {name}")
            task["func"](*task["args"], **task["kwargs"])
            self.completed_tasks.append(name)
            print(f"[COMPLETED] {name}")
            self.memory.store_task(name, "success")
        except Exception as e:
            print(f"[ERROR] {name} → {e}")
            self.memory.store_task(name, "failed", str(e))

    # ------------------------------
    # 3. Worker for threading
    # ------------------------------
    def worker(self):
        while not self.task_queue.empty():
            task = self.task_queue.get()
            self.execute_task(task)
            self.task_queue.task_done()

    # ------------------------------
    # 4. Run all tasks
    # ------------------------------
    def run_all(self, threads=1):
        print(f"[INFO] Running all tasks with {threads} thread(s)...")
        thread_list = []
        for _ in range(threads):
            t = Thread(target=self.worker)
            t.start()
            thread_list.append(t)

        for t in thread_list:
            t.join()
        print("[SUCCESS] All tasks completed.")

# ------------------------------
# 5. Example placeholder tasks
# ------------------------------
def example_task_download_model(model_name):
    print(f"Downloading {model_name} (placeholder)...")
    # Replace with real download logic if needed

def example_task_create_project(project_name):
    print(f"Creating project folder {project_name} (placeholder)...")
    os.makedirs(os.path.expanduser(f"~/CalebStudioProjects/{project_name}"), exist_ok=True)

# ------------------------------
# 6. Test run
# ------------------------------
if __name__ == "__main__":
    tm = TaskManager()
    tm.add_task("Download SD 1.5", example_task_download_model, "stable_diffusion_1.5")
    tm.add_task("Create Demo Project", example_task_create_project, "DemoProject")
    tm.run_all(threads=2)
