from urllib.parse import quote_plus
import datetime

from bson.objectid import ObjectId
from configuration import conf
from motor import motor_asyncio
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    def __init__(self):
        print(f"Connecting to MongoDB: {conf.db.uri}")
        self.client = motor_asyncio.AsyncIOMotorClient(conf.db.uri)
        self.db = self.client[conf.db.database]
        logger.info(f"Connected to MongoDB: {conf.db.uri}")

    async def get_user(self, user_id):
        """Get user by Telegram ID, compatible with User model"""
        return await self.db.users.find_one({"user_id": user_id})

    async def user_update(self, user_id, data=None):
        """
        Update user data, maintaining compatibility with User model
        """
        user_info = await self.get_user(user_id)
        if user_info is None:
            # Create new user record with basic fields and timestamp
            now = datetime.datetime.now(datetime.timezone.utc)
            await self.db.users.insert_one({
                "user_id": user_id,
                "created_at": now,
                "updated_at": now
            })
            return await self.user_update(user_id, data)

        if data:
            # Update timestamp when modifying user data
            data["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
            await self.db.users.update_one(
                {"user_id": user_id}, {"$set": data}, upsert=True
            )
            return await self.get_user(user_id)

        return user_info

    async def users_list(self):
        return await self.db.users.find().to_list(length=None)

    async def get_nominations(self):
        return await self.db.nominations.find().to_list(length=None)

    async def get_nomination(self, nomination_id):
        if isinstance(nomination_id, str) and ObjectId.is_valid(nomination_id):
            nomination_id = ObjectId(nomination_id)
        return await self.db.nominations.find_one({"_id": nomination_id})

    async def get_participants(self, nomination_id=None):
        filter_query = {}
        if nomination_id:
            if isinstance(nomination_id, str) and ObjectId.is_valid(nomination_id):
                nomination_id = ObjectId(nomination_id)
            filter_query["_id"] = nomination_id
        
        nominations = await self.db.nominations.find(filter_query).to_list(length=None)
        participants = []
        for nomination in nominations:
            if "participants" in nomination:
                participants.extend(nomination["participants"])

        return participants
    
    async def add_vote(self, nomination_id, participant_name, user_id):
        """
        Record a vote, structured to maintain compatibility with Vote model
        """
        if isinstance(nomination_id, str) and ObjectId.is_valid(nomination_id):
            nomination_id = ObjectId(nomination_id)
        
        # Ensure user exists
        user = await self.get_user(user_id)
        if not user:
            return False, "User not found"
            
        # Check for existing vote
        existing_vote = await self.db.votes.find_one({
            "nomination_id": nomination_id,
            "user_id": user_id
        })
        
        if existing_vote and existing_vote.get("participant_name") == participant_name:
            return False, "🚨 Siz ushbu ishtirokchi uchun allaqachon ovoz bergansiz! Boshqa ishtirokchiga ovoz bermoqchimisiz?"
        
        # Handle vote change
        if existing_vote:
            previous_participant = existing_vote.get("participant_name")
            await self.db.nominations.update_one(
                {
                    "_id": nomination_id,
                    "participants.name": previous_participant
                },
                {"$inc": {"participants.$.votes": -1}}
            )
            await self.db.votes.delete_one({"_id": existing_vote["_id"]})
        
        # Create new vote with fields compatible with Vote model
        now = datetime.datetime.now(datetime.timezone.utc)
        vote = {
            "nomination_id": nomination_id,
            "participant_name": participant_name,
            "user_id": user_id,
            "voted_at": now
        }
        await self.db.votes.insert_one(vote)
        
        # Update participant vote count
        await self.db.nominations.update_one(
            {
                "_id": nomination_id,
                "participants.name": participant_name
            },
            {"$inc": {"participants.$.votes": 1}}
        )
        
        # Generate appropriate message
        message = "🎯 Ajoyib tanlov! Ovozingiz muvaffaqiyatli qabul qilindi."
        if existing_vote:
            message = f"🔄 Sizning ovozingiz {existing_vote.get('participant_name')} ishtirokchisidan {participant_name} ishtirokchisiga muvofaqqiyatli o'zgartirildi!"
            
        return True, message


db = MongoDB()