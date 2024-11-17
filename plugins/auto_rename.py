from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from helper.database import AshutoshGoswami24
import asyncio
from queue import Queue
from threading import Thread

@Client.on_message(filters.private & filters.command("autorename"))
async def auto_rename_command(client, message):
    user_id = message.from_user.id

    # Extract the format from the command
    format_template = message.text.split("/autorename", 1)[1].strip()

    # Save the format template to the database
    await AshutoshGoswami24.set_format_template(user_id, format_template)

    await message.reply_text("**Auto Rename Format Updated Successfully! ✅**")

@Client.on_message(filters.private & filters.command("setmedia"))
async def set_media_command(client, message):
    user_id = message.from_user.id    
    media_type = message.text.split("/setmedia", 1)[1].strip().lower()

    # Save the preferred media type to the database
    await AshutoshGoswami24.set_media_preference(user_id, media_type)

    await message.reply_text(f"**Media Preference Set To :** {media_type} ✅")

# Define the file renaming queue
file_queue = Queue()
MAX_BATCH_SIZE = 5

# Function to rename a single file
async def rename_file(file):
    try:
        # Add your renaming logic here
        print(f"Renaming file: {file}")
        await asyncio.sleep(2)  # Simulate processing time
    except Exception as e:
        print(f"Error renaming file {file}: {e}")

# Worker function to process files from the queue in batches
async def process_queue():
    while True:
        if not file_queue.empty():
            batch = []
            while not file_queue.empty() and len(batch) < MAX_BATCH_SIZE:
                batch.append(file_queue.get())

            # Process the batch
            for file in batch:
                await rename_file(file)
                file_queue.task_done()

            print("Batch processed. Waiting for the next batch...")
        else:
            await asyncio.sleep(1)  # Wait before checking the queue again

# Add files to the queue
def add_files_to_queue(files):
    for file in files:
        file_queue.put(file)
        print(f"Added {file} to the queue")

# Start the queue processing loop in the background
def start_queue_processor():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_queue())

# Start the queue processor in a background thread
Thread(target=start_queue_processor, daemon=True).start()






