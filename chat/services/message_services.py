from chat.models import User, Chat, Message




def send_message(sender: User, content:str, chat: Chat):
    """
    Xabar yuborish funksiyasi.
    
    :parametr sender: Xabar yuboruvchi foydalanuvchi
    :parametr content: Xabar matni
    :parametr chat: Xabar yuboriladigan chat
    """
    