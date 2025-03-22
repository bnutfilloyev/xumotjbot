import mongoengine as db
from datetime import datetime, timezone
from typing import List


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