from typing import Optional, List, Tuple
import logging

from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ..models import User
from chat.models import User, Profile, FriendRequest, Notification

logger = logging.getLogger(__name__)


def get_profile(user: User, create_if_missing: bool = False) -> Optional[Profile]:
    """
    Return the Profile for the given user.

    If create_if_missing is True, creates and returns a Profile when none exists.
    Returns None when profile is missing and create_if_missing is False.
    """
    try:
        return Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        if create_if_missing:
            return Profile.objects.create(user=user)
        logger.debug("Profile does not exist for user id=%s", getattr(user, "id", None))
        return None


def update_profile(user: User, data: dict, allowed_fields: Optional[List[str]] = None) -> Profile:
    """
    Update user's profile with provided data.

    - allowed_fields: optional whitelist of profile fields that can be updated.
    - Raises ValueError on invalid input or ValidationError from model cleaning.
    """
    profile = get_profile(user, create_if_missing=True)
    if profile is None:
        raise ValueError("Unable to obtain or create profile for user.")

    if allowed_fields is None:
        # adjust allowed fields to your Profile model actual fields
        allowed_fields = ["bio", "age", "image", "display_name"]

    changed = False
    for field, value in data.items():
        if field in allowed_fields and hasattr(profile, field):
            setattr(profile, field, value)
            changed = True
        else:
            logger.debug("Attempt to update disallowed or unknown field '%s' on Profile", field)

    if not changed:
        logger.debug("No allowed fields provided to update for user id=%s", getattr(user, "id", None))
        return profile

    # Optional: validate before saving
    try:
        profile.full_clean()
    except ValidationError as e:
        logger.warning("Profile validation failed for user id=%s: %s", getattr(user, "id", None), e)
        raise

    profile.save(update_fields=[f for f in allowed_fields if hasattr(profile, f)])
    return profile


def send_friend_request(from_user: User, to_user: User) -> FriendRequest:
    """
    Create a friend request from from_user to to_user.

    - Prevents sending request to self.
    - Uses get_or_create to avoid duplicates (honors unique_together on the model).
    - Returns the FriendRequest instance (existing or newly created).
    - May raise IntegrityError on DB constraint failures.
    """
    if from_user == to_user:
        raise ValueError("Cannot send friend request to yourself.")

    # Prevent duplicate by get_or_create, handle race with transaction
    try:
        with transaction.atomic():
            fr, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
            if not created:
                logger.debug(
                    "FriendRequest already exists: %s -> %s",
                    getattr(from_user, "id", str(from_user)),
                    getattr(to_user, "id", str(to_user)),
                )
            return fr
    except IntegrityError as e:
        logger.error("IntegrityError creating FriendRequest: %s", e)
        raise


def get_friends(user: User) -> List[User]:
    """
    Return a list of User objects that are considered 'friends'.

    Behavior depends on FriendRequest model:
    - If FriendRequest has an 'accepted' / 'is_accepted' boolean field, uses that.
    - Otherwise treats mutual requests (A->B and B->A exist) as friends.
    """
    # Prefer explicit accepted field if present
    accepted_field = None
    if hasattr(FriendRequest, "accepted"):
        accepted_field = "accepted"
    elif hasattr(FriendRequest, "is_accepted"):
        accepted_field = "is_accepted"

    if accepted_field:
        sent = FriendRequest.objects.filter(from_user=user, **{accepted_field: True}).values_list("to_user", flat=True)
        received = FriendRequest.objects.filter(to_user=user, **{accepted_field: True}).values_list("from_user", flat=True)
        user_ids = set(list(sent) + list(received))
        return list(User.objects.filter(id__in=user_ids))

    # Fallback: mutual requests imply friendship
    sent_to_ids = FriendRequest.objects.filter(from_user=user).values_list("to_user", flat=True)
    mutual_ids = FriendRequest.objects.filter(from_user__in=sent_to_ids, to_user=user).values_list("from_user", flat=True)
    return list(User.objects.filter(id__in=set(mutual_ids)))


def get_notifications(user: User):
    """
    Return all notifications for a user ordered newest-first.
    """
    return Notification.objects.filter(user=user).order_by("-created_at")


def mark_notification_as_read(notification_id: int) -> Optional[Notification]:
    """
    Mark Notification as read. Returns the Notification or None if not found.
    """
    try:
        notif = Notification.objects.get(id=notification_id)
        if not notif.is_read:
            notif.is_read = True
            notif.save(update_fields=["is_read"])
        return notif
    except Notification.DoesNotExist:
        logger.debug("Notification id=%s not found when marking read", notification_id)
        return None


def delete_notification(notification_id: int) -> bool:
    """
    Delete a notification by id. Returns True if deleted, False if not found.
    """
    try:
        notif = Notification.objects.get(id=notification_id)
        notif.delete()
        return True
    except Notification.DoesNotExist:
        logger.debug("Attempted to delete non-existent notification id=%s", notification_id)
        return False



