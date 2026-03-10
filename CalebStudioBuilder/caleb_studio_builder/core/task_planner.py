import os
import json
from datetime import datetime

class TaskPlanner:
    def __init__(self, plan_dir="caleb_memory/plans"):
        self.plan_dir = os.path.abspath(plan_dir)
        os.makedirs(self.plan_dir, exist_ok=True)
        self.task_queue = []
        self.max_queue_size = 20

    def create_plan(self, objective, steps):
        """Generates a structured plan file before execution."""
        if len(steps) > 10:
            print("[!] Warning: Plan exceeds max_plan_steps (10). Truncating.")
            steps = steps[:10]
            
        plan_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_file = os.path.join(self.plan_dir, f"plan_{plan_id}.json")
        
        plan_data = {
            "objective": objective,
            "status": "pending",
            "steps": steps,
            "created_at": plan_id
        }
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, indent=4)
            
        return plan_file

    def enqueue_task(self, task):
        """Adds a task to the execution queue."""
        if len(self.task_queue) >= self.max_queue_size:
            print("[!] Task queue full. Cannot add task.")
            return False
        self.task_queue.append({"task": task, "retries": 0, "status": "queued"})
        return True

    def get_next_task(self):
        """Retrieves the next pending task."""
        for task in self.task_queue:
            if task["status"] in ["queued", "failed"] and task["retries"] < 3:
                return task
        return None

if __name__ == "__main__":
    planner = TaskPlanner()
    plan_path = planner.create_plan("Bootstrap GUI", ["Build top bar", "Build splitters", "Link logs"])
    planner.enqueue_task("Execute Step 1")
    print(f"Task Planner initialized. Test plan created at: {plan_path}")
    print(f"Next task in queue: {planner.get_next_task()}")
