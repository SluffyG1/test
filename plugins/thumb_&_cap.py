from pyrogram import Client, filters
from helper.database import AshutoshGoswami24


@Client.on_message(filters.private & filters.command("set_caption"))
async def add_caption(client, message):
    if len(message.command) == 1:
        return await message.reply_text(
            "**Give The Caption\n\nExample :- `/set_caption 📕Name ➠ : {filename} \n\n🔗 Size ➠ : {filesize} \n\n⏰ Duration ➠ : {duration}`**"
        )
    caption = message.text.split(" ", 1)[1]
    try:
        await AshutoshGoswami24.set_caption(message.from_user.id, caption=caption)
        await message.reply_text("**Your Caption Successfully Added ✅**")
    except Exception as e:
        logging.error(f"Error setting caption for user {message.from_user.id}: {e}")
        await message.reply_text("**An error occurred. Please try again later.**")


@Client.on_message(filters.private & filters.command("del_caption"))
async def delete_caption(client, message):
    caption = await AshutoshGoswami24.get_caption(message.from_user.id)
    if not caption:
        return await message.reply_text("**You Don't Have Any Caption ❌**")
    await AshutoshGoswami24.set_caption(message.from_user.id, caption=None)
    await message.reply_text("**Your Caption Successfully Deleted 🗑️**")


@Client.on_message(filters.private & filters.command(["see_caption", "view_caption"]))
async def see_caption(client, message):
    caption = await AshutoshGoswami24.get_caption(message.from_user.id)
    if caption:
        await message.reply_text(f"**Your Caption :**\n\n`{caption}`")
    else:
        await message.reply_text("**You Don't Have Any Caption ❌**")


@Client.on_message(filters.private & filters.command(["view_thumb", "viewthumb"]))
async def viewthumb(client, message):
    thumb = await AshutoshGoswami24.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb)
    else:
        await message.reply_text("**You Don't Have Any Thumbnail ❌**")


@Client.on_message(filters.private & filters.command(["del_thumb", "delthumb"]))
async def removethumb(client, message):
    await AshutoshGoswami24.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("**Thumbnail Deleted Successfully 🗑️**")


@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    try:
        await AshutoshGoswami24.set_thumbnail(message.from_user.id, file_id=message.photo.file_id)
        await message.reply_text("**Thumbnail Saved Successfully ✅️**")
    except Exception as e:
        logging.error(f"Error setting thumbnail for user {message.from_user.id}: {e}")
        await message.reply_text("**An error occurred while saving the thumbnail. Please try again later.**")
