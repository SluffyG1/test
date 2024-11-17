import logging
import warnings
from pyrogram import Client, idle
from pyrogram import __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from pytz import timezone
from datetime import datetime
import asyncio
from plugins.web_support import web_server
import pyromod
from plugins.auto_rename import start_queue_processor, add_files_to_queue

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="AshutoshGoswami24",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )
        self.app = None  # Initialize app as an instance variable

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username

        # Define app here
        self.app = web.AppRunner(await web_server())
        await self.app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(self.app, bind_address, Config.PORT).start()

        logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")

        for id in Config.ADMIN:
            try:
                await self.send_message(
                    id, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**"
                )
            except:
                pass

        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime("%d %B, %Y")
                time = curr.strftime("%I:%M:%S %p")
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n📅 Dᴀᴛᴇ : `{date}`\n⏰ Tɪᴍᴇ : `{time}`\n🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\🤖 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`</b>",
                )
            except:
                print("Pʟᴇᴀꜱᴇ Mᴀᴋᴇ Tʜɪꜱ Iꜱ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Lᴏɢ Cʜᴀɴɴᴇʟ")

    async def stop(self, *args):
        if self.app:
            await self.app.cleanup()  # Clean up the app when stopping
        await super().stop()
        logging.info("Bot Stopped 🙄")

bot_instance = Bot()

def main():
    async def start_services():
        if Config.STRING_SESSION:
            await asyncio.gather(
                bot_instance.start(),  # Start the bot instance
            )
        else:
            await asyncio.gather(bot_instance.start())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_services())
    loop.run_forever()

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="There is no current event loop")
    main()

# Bot initialization logic
def initialize_bot():
    print("Starting the bot...")

    # Start the queue processor
    start_queue_processor()

    # Example: Simulate adding files to the queue from the bot
    files = ["bot_file1", "bot_file2", "bot_file3", "bot_file4", "bot_file5"]
    add_files_to_queue(files)
    print("Files added to the queue from the bot.")

if __name__ == "__main__":
    initialize_bot()

