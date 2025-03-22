"""
Admin UI views for XumotjBot Admin Panel.
"""
from starlette_admin.contrib.mongoengine import ModelView
from database import Nomination


class NominationView(ModelView):
    """Enhanced view for Nomination model with participant information."""
    list_display = ["title", "description", "is_active", "created_at", "updated_at"]
    search_fields = ["title", "description"]
    sortable_fields = ["title", "is_active", "created_at", "updated_at"]
    filters = ["is_active", "created_at", "updated_at"]
