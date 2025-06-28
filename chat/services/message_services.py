from chat.models import User, Chat, Message




def send_message(sender: User, content:str, chat: Chat):
    """
    Xabar yuborish funksiyasi.
    
    :parametr sender: Xabar yuboruvchi foydalanuvchi
    :parametr content: Xabar matni
    :parametr chat: Xabar yuboriladigan chat
    """
    message = Message.objects.create(sender=sender, content=content, chat=chat)  
    return message
     
def get_chat_messages(chat: Chat):
    pass


def mark_message_as_read(message: Message):
    pass 


def delete_message(message: Message):
    pass


def edit_message(message: Message, new_content: str):
    pass




