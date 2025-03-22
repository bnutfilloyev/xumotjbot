"""
Admin UI views for XumotjBot Admin Panel.
"""
from starlette_admin.contrib.mongoengine import ModelView
from database import Nomination, User, Vote


class NominationView(ModelView):
    """Enhanced view for Nomination model with participant information."""
    list_display = ["title", "description", "is_active", "created_at", "updated_at"]
    search_fields = ["title", "description"]
    sortable_fields = ["title", "is_active", "created_at", "updated_at"]
    filters = ["is_active", "created_at", "updated_at"]


class UserView(ModelView):
    """View for managing Telegram users."""
    list_display = ["user_id", "fullname", "username", "input_fullname", "input_phone", "created_at"]
    search_fields = ["fullname", "username", "input_fullname", "input_phone"]
    sortable_fields = ["user_id", "fullname", "created_at", "updated_at"]
    filters = ["created_at", "updated_at"]
    readonly_fields = ["user_id", "created_at", "updated_at"]


class VoteView(ModelView):
    """View for monitoring voting activity."""
    list_display = ["user", "nomination", "participant_name", "voted_at"]
    search_fields = ["participant_name"]
    sortable_fields = ["voted_at"]
    filters = ["nomination", "voted_at"]
