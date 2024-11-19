import motor.motor_asyncio
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError
from pydantic import BaseModel, ValidationError
from config import Config
import logging
from helper.queue_utils import add_files_to_queue
from helper.utils import send_log  # Assuming `send_log` sends logs to a logging channel or service

# Configure logging
logging.basicConfig(level=logging.INFO)

class UserSchema(BaseModel):
    """Schema validation for user documents."""
    _id: int
    file_id: str | None = None
    caption: str | None = None
    metadata: bool = True
    metadata_code: str = "Telegram : @AshutoshGoswami24"
    format_template: str | None = None
    media_type: str | None = None


class Database:
    """Database class to handle MongoDB operations."""
    
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
        self.file_tasks_col = self.db.file_tasks  # Collection for file task management

    def new_user(self, id: int):
        """Create a new user document."""
        return {
            "_id": id,
            "file_id": None,
            "caption": None,
            "metadata": True,
            "metadata_code": "Telegram : @AshutoshGoswami24",
            "format_template": None,
            "media_type": None,
        }

    async def add_user(self, b, m):
        """Add a new user to the database."""
        user_id = m.from_user.id
        if not await self.is_user_exist(user_id):
            user = self.new_user(user_id)
            try:
                validated_user = UserSchema(**user)  # Validate using schema
                await self.col.insert_one(validated_user.dict())
                await send_log(b, m.from_user)
                logging.info(f"Added new user {user_id}")
            except ValidationError as ve:
                logging.error(f"Validation error for user {user_id}: {ve}")
            except PyMongoError as e:
                logging.error(f"Error adding user {user_id}: {e}")

    async def is_user_exist(self, id: int) -> bool:
        """Check if a user exists in the database."""
        try:
            return bool(await self.col.find_one({"_id": id}))
        except PyMongoError as e:
            logging.error(f"Error checking user {id}: {e}")
            return False

    async def total_users_count(self) -> int:
        """Get total user count."""
        try:
            return await self.col.count_documents({})
        except PyMongoError as e:
            logging.error(f"Error counting users: {e}")
            return 0

    async def get_all_users(self, limit: int = 100, skip: int = 0):
        """Fetch all users with pagination."""
        try:
            cursor = self.col.find({}).skip(skip).limit(limit)
            return [user async for user in cursor]
        except PyMongoError as e:
            logging.error(f"Error retrieving all users: {e}")
            return []

    async def delete_user(self, user_id: int):
        """Delete a user."""
        try:
            await self.col.delete_one({"_id": user_id})
            logging.info(f"Deleted user {user_id}")
        except PyMongoError as e:
            logging.error(f"Error deleting user {user_id}: {e}")

    async def set_property(self, id: int, property_name: str, value):
        """Set a specific property for a user."""
        try:
            await self.col.update_one({"_id": id}, {"$set": {property_name: value}})
            logging.info(f"Set {property_name} for user {id}")
        except PyMongoError as e:
            logging.error(f"Error setting {property_name} for user {id}: {e}")

    async def get_property(self, id: int, property_name: str, default_value=None):
        """Get a specific property for a user."""
        try:
            user = await self.col.find_one({"_id": id})
            return user.get(property_name, default_value) if user else default_value
        except PyMongoError as e:
            logging.error(f"Error getting {property_name} for user {id}: {e}")
            return default_value

    async def set_metadata(self, id: int, metadata_value: bool):
        """Set metadata for a user."""
        await self.set_property(id, "metadata", metadata_value)

    async def get_metadata(self, id: int):
        """Get metadata for a user."""
        return await self.get_property(id, "metadata", default_value=True)

    # File Task Management
    async def fetch_files_from_db(self, batch_size: int = 5):
        """Fetch files to rename from the database."""
        try:
            cursor = self.file_tasks_col.find({"status": "pending"}).limit(batch_size)
            return [file async for file in cursor]
        except PyMongoError as e:
            logging.error(f"Error fetching files: {e}")
            return []

    async def mark_files_as_processed(self, file_ids: list[str]):
        """Mark files as processed."""
        try:
            await self.file_tasks_col.update_many(
                {"_id": {"$in": file_ids}}, {"$set": {"status": "processed"}}
            )
            logging.info(f"Marked {len(file_ids)} files as processed.")
        except PyMongoError as e:
            logging.error(f"Error marking files as processed: {e}")

    # Example: Fetch and add files to the queue
    async def process_file_tasks(self):
        """Fetch and add pending files to the rename queue."""
        files = await self.fetch_files_from_db(batch_size=20)
        if files:
            filenames = [file["filename"] for file in files]
            add_files_to_queue(filenames)  # Add to the queue
            await self.mark_files_as_processed([file["_id"] for file in files])
            logging.info("Pending files added to the queue.")
        else:
            logging.info("No pending files to process.")


# Singleton database instance
AshutoshGoswami24 = Database(Config.DB_URL, Config.DB_NAME)
