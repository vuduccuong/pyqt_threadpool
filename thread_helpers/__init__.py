import queue
import threading


class ThreadPool:
    def __init__(self, num_threads):
        self.task_queue = queue.Queue()
        self.threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=self.run_tasks)
            self.threads.append(thread)
            thread.start()

    def add_task(self, task):
        self.task_queue.put(task)

    def run_tasks(self):
        while self.task_queue.not_empty:
            task = self.task_queue.get()
            task.finished.connect()
            task.run()
            self.task_queue.task_done()
