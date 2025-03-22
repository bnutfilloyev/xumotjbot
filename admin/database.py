import mongoengine as db
from datetime import datetime, timezone
from typing import List, Optional


class Participant(db.EmbeddedDocument):
    """
    Represents a participant in a nomination.
    
    Attributes:
        name (str): The name of the participant
        votes (int): The number of votes the participant has received
        created_at (datetime): When the participant was added
    """
    name = db.StringField(required=True, max_length=100)
    votes = db.IntField(default=0, min_value=0)
    created_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    def increment_vote(self) -> None:
        """Increment the vote count by 1."""
        self.votes += 1
    
    def __str__(self) -> str:
        return f"{self.name} ({self.votes} votes)"


class Nomination(db.Document):
    """
    Represents a nomination category with participants.
    
    Attributes:
        title (str): The title of the nomination
        description (str): Optional description of the nomination
        participants (List[Participant]): List of participants in this nomination
        is_active (bool): Whether voting is currently active for this nomination
        created_at (datetime): When the nomination was created
        updated_at (datetime): When the nomination was last updated
    """
    title = db.StringField(required=True, max_length=200, unique=True)
    description = db.StringField(max_length=500)
    participants = db.ListField(db.EmbeddedDocumentField(Participant), default=[])
    is_active = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {
        'indexes': [
            {'fields': ['title'], 'unique': True},
            {'fields': ['is_active']},
            {'fields': ['-created_at']}
        ],
        'ordering': ['-created_at'],
        'collection': 'nominations'
    }
    
    def add_participant(self, name: str) -> Participant:
        """
        Add a new participant to the nomination.
        
        Args:
            name: The name of the participant
            
        Returns:
            The newly created participant
        """
        participant = Participant(name=name)
        self.participants.append(participant)
        self.updated_at = datetime.now(timezone.utc)
        self.save()
        return participant
    
    def vote_for_participant(self, participant_name: str) -> bool:
        """
        Register a vote for a participant.
        
        Args:
            participant_name: The name of the participant to vote for
            
        Returns:
            True if the vote was successful, False otherwise
        """
        if not self.is_active:
            return False
            
        for i, participant in enumerate(self.participants):
            if participant.name == participant_name:
                self.participants[i].increment_vote()
                self.updated_at = datetime.now(timezone.utc)
                self.save()
                return True
        return False
    
    def get_results(self) -> List[Participant]:
        """
        Get participants sorted by votes (highest first).
        
        Returns:
            Sorted list of participants
        """
        return sorted(self.participants, key=lambda p: p.votes, reverse=True)
    
    def __str__(self) -> str:
        return f"{self.title} ({len(self.participants)} participants)"


class User(db.Document):
    """
    Represents a Telegram user who has interacted with the bot.
    Maps directly to the users collection created by the bot.
    """
    user_id = db.IntField(required=True, unique=True)
    fullname = db.StringField(max_length=255)
    username = db.StringField(max_length=64)
    input_fullname = db.StringField(max_length=255)
    input_phone = db.StringField(max_length=20)
    created_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {
        'indexes': [
            {'fields': ['user_id'], 'unique': True},
            {'fields': ['username']},
            {'fields': ['input_phone']},
            {'fields': ['-created_at']}
        ],
        'collection': 'users',  # Important: matches the bot's collection name
        'ordering': ['-created_at']
    }
    
    @classmethod
    def get_or_create(cls, user_id: int, fullname: str = None, username: str = None) -> 'User':
        user = cls.objects(user_id=user_id).first()
        if user:
            if (fullname and user.fullname != fullname) or (username and user.username != username):
                user.fullname = fullname or user.fullname
                user.username = username or user.username
                user.updated_at = datetime.now(timezone.utc)
                user.save()
            return user
        user = cls(user_id=user_id, fullname=fullname, username=username)
        user.save()
        return user
    
    def update_registration_info(self, input_fullname: str = None, input_phone: str = None) -> None:
        if input_fullname:
            self.input_fullname = input_fullname
        if input_phone:
            self.input_phone = input_phone
        self.updated_at = datetime.now(timezone.utc)
        self.save()
    
    def is_fully_registered(self) -> bool:
        return bool(self.input_fullname and self.input_phone)
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "fullname": self.fullname,
            "username": self.username,
            "input_fullname": self.input_fullname,
            "input_phone": self.input_phone,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_registered": self.is_fully_registered(),
        }
    
    def __str__(self) -> str:
        return f"User {self.fullname or self.username or self.user_id}"


class Vote(db.Document):
    """
    Represents a vote cast by a user for a participant in a nomination.
    Note: Modified to match the structure used by the bot's database functions.
    """
    user_id = db.IntField(required=True)
    nomination_id = db.ObjectIdField(required=True)
    participant_name = db.StringField(required=True, max_length=100)
    voted_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {
        'indexes': [
            {'fields': ['user_id', 'nomination_id'], 'unique': True},
            {'fields': ['-voted_at']}
        ],
        'collection': 'votes',  # Important: matches the bot's collection name
        'ordering': ['-voted_at']
    }
    
    @property
    def user(self):
        """Get the user who cast this vote"""
        return User.objects(user_id=self.user_id).first()
        
    @property
    def nomination(self):
        """Get the nomination for this vote"""
        return Nomination.objects(id=self.nomination_id).first()
    
    @classmethod
    def cast_vote(cls, user_id: int, nomination_id: str, participant_name: str) -> tuple:
        user = User.objects(user_id=user_id).first()
        if not user:
            return False, "User not found"
        nomination = Nomination.objects(id=nomination_id).first()
        if not nomination:
            return False, "Nomination not found"
        if not nomination.is_active:
            return False, "Voting is closed for this nomination"
        participant_exists = any(p.name == participant_name for p in nomination.participants)
        if not participant_exists:
            return False, "Participant not found"
        existing_vote = cls.objects(user_id=user_id, nomination_id=nomination_id).first()
        if existing_vote and existing_vote.participant_name == participant_name:
            return False, "You've already voted for this participant"
        if existing_vote:
            for i, p in enumerate(nomination.participants):
                if p.name == existing_vote.participant_name:
                    nomination.participants[i].votes = max(0, nomination.participants[i].votes - 1)
                    break
            existing_vote.delete()
        vote = cls(user_id=user_id, nomination_id=nomination_id, participant_name=participant_name)
        vote.save()
        for i, p in enumerate(nomination.participants):
            if p.name == participant_name:
                nomination.participants[i].votes += 1
                break
        nomination.updated_at = datetime.now(timezone.utc)
        nomination.save()
        if existing_vote:
            return True, f"Vote changed from {existing_vote.participant_name} to {participant_name}"
        return True, "Vote recorded successfully"