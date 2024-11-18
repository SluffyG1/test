from queue import Queue

file_queue = Queue()
MAX_BATCH_SIZE = 5

def add_files_to_queue(files):
    for file in files:
        file_queue.put(file)
        print(f"Added {file} to the queue")
