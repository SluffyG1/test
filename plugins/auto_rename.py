from pyrogram import Client, filters
import asyncio
from threading import Thread
from helper.database import AshutoshGoswami24
from helper.queue_utils import add_files_to_queue, process_queue
import logging

# Command to set auto-rename format
@Client.on_message(filters.private & filters.command("autorename"))
async def auto_rename_command(client, message):
    """Set a custom renaming format for the user."""
    try:
        user_id = message.from_user.id
        format_template = message.text.split("/autorename", 1)[1].strip()

        if not format_template:
            await message.reply_text("❌ Please provide a valid format template!")
            return

        # Save the format_template to the database or state
        await message.reply_text("✅ **Auto Rename Format Updated Successfully!**")
        logging.info(f"Set rename format for user {user_id}: {format_template}")
    except IndexError:
        await message.reply_text("❌ Usage: /autorename <template>")
    except Exception as e:
        logging.error(f"Error in autorename command: {e}")
        await message.reply_text("❌ An error occurred while updating format!")

# Command to set preferred media type
@Client.on_message(filters.private & filters.command("setmedia"))
async def set_media_command(client, message):
    """Set the user's preferred media type for processing."""
    try:
        user_id = message.from_user.id
        media_type = message.text.split("/setmedia", 1)[1].strip().lower()

        if media_type not in ["photo", "video", "document"]:
            await message.reply_text("❌ Invalid media type. Please use 'photo', 'video', or 'document'.")
            return

        # Save the media preference to the database or state
        await message.reply_text(f"✅ **Media Preference Set To:** {media_type}")
        logging.info(f"Set media preference for user {user_id}: {media_type}")
    except IndexError:
        await message.reply_text("❌ Usage: /setmedia <media_type>")
    except Exception as e:
        logging.error(f"Error in setmedia command: {e}")
        await message.reply_text("❌ An error occurred while setting media type!")

# Automatically add files to the queue when they are sent to the bot
@Client.on_message(filters.private & filters.document | filters.photo | filters.video)
async def handle_file_upload(client, message):
    """Automatically add uploaded files to the processing queue."""
    try:
        user_id = message.from_user.id
        file_id = None

        # Determine the file type and extract file_id
        if message.document:
            file_id = message.document.file_id
        elif message.photo:
            file_id = message.photo.file_id
        elif message.video:
            file_id = message.video.file_id

        if file_id:
            # Add the file to the queue
            add_files_to_queue([file_id])
            await message.reply_text(f"✅ Your file has been added to the processing queue.")
            logging.info(f"User {user_id} uploaded file {file_id} added to the queue.")
    except Exception as e:
        logging.error(f"Error handling file upload: {e}")
        await message.reply_text("❌ Failed to add your file to the queue.")

# File renaming logic
async def rename_file(file_id):
    """Simulate the file renaming process."""
    try:
        logging.info(f"Renaming file: {file_id}")
        await asyncio.sleep(2)  # Simulate renaming delay
        logging.info(f"File renamed successfully: {file_id}")
    except Exception as e:
        logging.error(f"Error renaming file {file_id}: {e}")

# Start the queue processor in a background thread
def start_queue_processor():
    """Run the queue processor in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_queue(rename_file))

Thread(target=start_queue_processor, daemon=True).start()

