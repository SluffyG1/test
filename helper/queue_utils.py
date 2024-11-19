import asyncio
import logging
from queue import Queue

file_queue = Queue()
MAX_BATCH_SIZE = 5  # Adjust as needed


def add_files_to_queue(files):
    """Add a list of files to the queue."""
    for file in files:
        file_queue.put(file)
        logging.info(f"Added file {file} to the queue")


def get_next_batch(queue, max_batch_size):
    """Retrieve the next batch of files from the queue."""
    batch = []
    while not queue.empty() and len(batch) < max_batch_size:
        batch.append(queue.get())
    return batch


async def process_queue(rename_file_func):
    """Continuously process the file queue using the provided renaming function."""
    while True:
        if not file_queue.empty():
            batch = get_next_batch(file_queue, MAX_BATCH_SIZE)
            logging.info(f"Processing batch of size {len(batch)}")
            for file in batch:
                try:
                    await rename_file_func(file)
                except Exception as e:
                    logging.error(f"Error processing file {file}: {e}")
                finally:
                    file_queue.task_done()
        else:
            await asyncio.sleep(1)  # Wait for new items in the queue
