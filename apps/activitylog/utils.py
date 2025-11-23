# apps/activity/utils.py
from .models import ActivityLog

def log_activity(family, user, action_type, target_type, target_id, description):
    ActivityLog.objects.create(
        family=family,
        user=user,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        description=description
        )