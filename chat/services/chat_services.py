from chat.models import Chat, User



def create_chat_service():
    pass


def get_user_chats_service(user):
    pass


def add_user_to_chat_service(chat_id, user_id):
    pass


def remove_user_from_chat_service(chat_id, user_id):
    pass


def delete_chat_service(chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)

    except Chat.DoesNotExist:
        
        pass
        
