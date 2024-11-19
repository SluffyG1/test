from pyrogram import Client, filters
import asyncio
from threading import Thread
from helper.database import AshutoshGoswami24
from helper.queue_utils import add_files_to_queue, process_queue
import logging

# Command to set auto-rename format
@Client.on_message(filters.private & filters.command("autorename"))
async def auto_rename_command(client, message):
    try:
        user_id = message.from_user.id
        format_template = message.text.split("/autorename", 1)[1].strip()

        if not format_template:
            await message.reply_text("❌ Please provide a valid format template!")
            return

        await AshutoshGoswami24.set_property(user_id, "format_template", format_template)
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
    try:
        user_id = message.from_user.id
        media_type = message.text.split("/setmedia", 1)[1].strip().lower()

        if media_type not in ["photo", "video"]:
            await message.reply_text("Invalid media type. Please use 'photo' or 'video'")
            return

        await AshutoshGoswami24.set_media_preference(user_id, media_type)
        await message.reply_text(f"✅ **Media Preference Set To:** {media_type}")
        logging.info(f"Set media preference for user {user_id}: {media_type}")
    except IndexError:
        await message.reply_text("❌ Usage: /setmedia <media_type>")
    except Exception as e:
        logging.error(f"Error in setmedia command: {e}")
        await message.reply_text("❌ An error occurred while setting media type!")

# File renaming logic
async def rename_file(file):
    try:
        logging.info(f"Renaming file: {file}")
        await asyncio.sleep(2)  # Simulate renaming delay
        logging.info(f"File renamed successfully: {file}")
    except Exception as e:
        logging.error(f"Error renaming file {file}: {e}")

# Start the queue processor in a background thread
def start_queue_processor():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_queue(rename_file))

Thread(target=start_queue_processor, daemon=True).start()
