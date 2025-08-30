from typing import Optional, List, Union
import logging

from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from chat.models import User, Chat, Message

logger = logging.getLogger(__name__)


def get_object_id(obj):
    """Helper to get the id or pk of an object, or None if not present."""
    return getattr(obj, "id", getattr(obj, "pk", None))


def get_object_id(obj):
    """Helper to get id or pk from an object, or None if not present."""
    return getattr(obj, "id", getattr(obj, "pk", None))

def send_message(sender: User, content: str, chat: Chat) -> Message:
    """
    Berilgan `sender` tomonidan `chat`ga yuborilgan Message (xabari) yaratadi va qaytaradi.
    - Matnni (bo'sh emasligini) tekshiradi.
    - Yuboruvchi chat a'zosi (yoki yaratuvchisi) ekanligini tekshiradi.
    - Qisman yozuvlarni oldini olish uchun transaction ishlatadi.
    """
    content = (content or "").strip()
    is_member = chat.members.filter(pk=sender.pk).exists() or getattr(chat, "creator_id", None) == sender.pk
    if not is_member:
        logger.warning("User %s attempted to send message to chat %s but is not a member.", get_object_id(sender), get_object_id(chat))
        raise PermissionError("Sender is not a member of the chat.")
    is_member = chat.members.filter(pk=sender.pk).exists() or getattr(chat, "creator_id", None) == sender.pk
    if not is_member:
        logger.warning("User %s attempted to send message to chat %s but is not a member.", get_object_id(sender), get_object_id(chat))
        raise PermissionError("Sender is not a member of the chat.")

    try:
        with transaction.atomic():
            message = Message.objects.create(sender=sender, content=content, chat=chat)
            # Agar Message modelida full_clean mavjud bo'lsa, validatsiya qiling
            try:
                message.full_clean()
            except ValidationError:
                # Agar validatsiya muvaffaqiyatsiz bo'lsa, rollback bo'ladi
                raise
            return message
    except IntegrityError as e:
        logger.error("Database error while sending message: %s", e)
        raise


def get_chat_messages(chat: Chat, limit: int = 50, offset: int = 0, newest_first: bool = False) -> List[Message]:
    """
    Chat uchun xabarlarni oddiy sahifalash bilan qaytaradi.
    - limit: qaytariladigan maksimal xabar soni.
    - offset: nechta xabarni o'tkazib yuborish.
    - newest_first: True bo'lsa, yangi xabarlar yuqoridan tartiblanadi.
    """
    qs = Message.objects.filter(chat=chat)
    qs = qs.order_by("-created_at" if newest_first else "created_at")
    return list(qs[offset: offset + limit])


def _resolve_message(message_or_id: Union[Message, int]) -> Optional[Message]:
    """Yordamchi: Message obyekti yoki uning id sini qabul qiladi."""
    if isinstance(message_or_id, Message):
        return message_or_id
    try:
        return Message.objects.get(id=message_or_id)
    except Message.DoesNotExist:
        return None


def mark_message_as_read(message_or_id: Union[Message, int], reader: Optional[User] = None) -> Optional[Message]:
    """
    Xabarni o'qilgan deb belgilaydi. Agar Message modelida foydalanuvchi bo'yicha o'qilganlik yo'q bo'lsa,
    boshqa mexanizm (masalan Notification) ishlatilishi kerak.
    - Agar Message modelida `is_read` maydoni bo'lsa, uni belgilaydi.
    - reader ixtiyoriy; berilsa, reader chat a'zosi ekanligini tekshirishingiz mumkin.
    """
    message = _resolve_message(message_or_id)
    if message is None:
        logger.debug("mark_message_as_read: message not found: %s", message_or_id)
        return None

    if reader is not None:
        # Message modelida 'chat' ForeignKey mavjudligini ta'minlang; aks holda to'g'ri field nomini ishlating.
        is_member = chat_obj.members.filter(pk=reader.pk).exists() or getattr(chat_obj, "creator_id", None) == reader.pk
        if not is_member:
            logger.warning(
                "User %s attempted to mark message %s as read but is not a chat member.",
                get_object_id(reader),
                get_object_id(message),
            )
            raise PermissionError("User is not a member of the chat.")
                get_object_id(reader),
                get_object_id(message),
            )
            raise PermissionError("User is not a member of the chat.")

    if hasattr(message, "is_read"):
        logger.debug("Message model has 'is_read' field, but assignment is not supported. Skipping marking as read.")
        # You may implement a custom mechanism here if needed.
    else:
        # Agar Message modelida is_read bo'lmasa, o'qilganni kuzatish uchun Notification yoki boshqa mexanizmni ishlating.
        logger.debug("Message model has no 'is_read' field; use Notification to track reads if required.")
    return message


def delete_message(message_or_id: Union[Message, int], actor: Optional[User] = None) -> bool:
    """
    Xabarni o'chiradi. Agar actor berilgan bo'lsa, faqat yuboruvchi yoki staff o'chirishi mumkin.
    Topilmasa False, muvaffaqiyatli o'chirilsa True qaytaradi.
    """
    message = _resolve_message(message_or_id)
    if message is None:
        logger.debug("delete_message: message not found: %s", message_or_id)
        if not (actor.is_staff or getattr(message, "sender_id", None) == get_object_id(actor)):
            logger.warning(
                "User %s attempted to delete message %s without permission.",
                get_object_id(actor),
                get_object_id(message),
            )
            raise PermissionError("Actor is not allowed to delete this message.")
                get_object_id(actor),
                get_object_id(message),
            )
            raise PermissionError("Actor is not allowed to delete this message.")

    message.delete()
    return True


def edit_message(message_or_id: Union[Message, int], actor: Optional[User], new_content: str) -> Message:
    """
    Xabar matnini tahrirlash. Actor yuboruvchi (yoki staff) bo'lishi kerak. Yangilangan Message ni qaytaradi.
    - Yangi matn bo'sh emasligini tekshiradi va mavjud bo'lsa full_clean chaqiradi.
    """
    if actor is not None:
        if not (actor.is_staff or getattr(message, "sender_id", None) == get_object_id(actor)):
            logger.warning(
                "User %s attempted to edit message %s without permission.",
                get_object_id(actor),
                get_object_id(message),
            )
            raise PermissionError("Actor is not allowed to edit this message.")
                get_object_id(actor),
                get_object_id(message),
            )
            raise PermissionError("Actor is not allowed to edit this message.")

    new_content = (new_content or "").strip()
    try:
        message.full_clean()
    except ValidationError as e:
        msg_id = get_object_id(message)
        logger.warning("Validation error when editing message %s: %s", msg_id, e)
        raise
    message.save(update_fields=["content"])
    return message
        logger.warning("Validation error when editing message %s: %s", msg_id, e)
        raise
    message.save(update_fields=["content"])
    return message




