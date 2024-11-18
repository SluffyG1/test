import motor.motor_asyncio
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError
from config import Config
import logging
from helper.queue_utils import add_files_to_queue
from helper.utils import send_log  # Assuming send_log is defined elsewhere


class Database:
    def __init__(self, uri, database_name):
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            self._client.server_info()  # Test connection
            logging.info("Successfully connected to MongoDB")
        except ServerSelectionTimeoutError as e:
            logging.error(f"MongoDB connection timeout: {e}")
            raise e
        except PyMongoError as e:
            logging.error(f"MongoDB connection failed: {e}")
            raise e

        self.db = self._client[database_name]
        self.col = self.db.user

    def new_user(self, id):
        return {
            "_id": int(id),
            "file_id": None,
            "caption": None,
            "metadata": True,
            "metadata_code": "Telegram : @AshutoshGoswami24",
            "format_template": None,
            "media_type": None,
        }

    async def add_user(self, b, m):
        user_id = m.from_user.id
        if not await self.is_user_exist(user_id):
            user = self.new_user(user_id)
            try:
                await self.col.insert_one(user)
                await send_log(b, m.from_user)
                logging.info(f"Added new user {user_id}")
            except PyMongoError as e:
                logging.error(f"Error adding user {user_id}: {e}")

    async def is_user_exist(self, id):
        try:
            return bool(await self.col.find_one({"_id": int(id)}))
        except PyMongoError as e:
            logging.error(f"Error checking user {id}: {e}")
            return False

    async def total_users_count(self):
        try:
            return await self.col.count_documents({})
        except PyMongoError as e:
            logging.error(f"Error counting users: {e}")
            return 0

    async def get_all_users(self):
        try:
            return self.col.find({})
        except PyMongoError as e:
            logging.error(f"Error retrieving all users: {e}")
            return None

    async def delete_user(self, user_id):
        try:
            await self.col.delete_many({"_id": int(user_id)})
            logging.info(f"Deleted user {user_id}")
        except PyMongoError as e:
            logging.error(f"Error deleting user {user_id}: {e}")

    async def set_property(self, id, property_name, value):
        try:
            await self.col.update_one({"_id": int(id)}, {"$set": {property_name: value}})
            logging.info(f"Set {property_name} for user {id}")
        except PyMongoError as e:
            logging.error(f"Error setting {property_name} for user {id}: {e}")

    async def get_property(self, id, property_name, default_value=None):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get(property_name, default_value) if user else default_value
        except PyMongoError as e:
            logging.error(f"Error getting {property_name} for user {id}: {e}")
            return default_value


# Singleton database instance
AshutoshGoswami24 = Database(Config.DB_URL, Config.DB_NAME)
