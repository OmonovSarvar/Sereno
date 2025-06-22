from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)  # Kim yozganini saqlaymiz
    content = models.TextField()                 # Xabar matni
    timestamp = models.DateTimeField(default=timezone.now)  # Vaqti

    def __str__(self):
        return f'{self.sender.username}: {self.content[:20]}'

    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    image = models.ImageField(upload_to='profile_pic/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True) # Optional text for bio
    
    def __str__(self):
        return self.user.username
    
class Attachment(models.Model):
    message = models.ForeignKey(Message, related_name='attachments', on_delete=models.CASCADE) # Xabarga bog'langan fayl
    file = models.FileField(upload_to='attachments/') # Faylni yuklash joyi
    uploaded_at = models.DateTimeField(auto_now_add=True) # Yuklangan vaqt
    added_by = models.ForeignKey(User, on_delete=models.CASCADE) # Kim yuklaganini saqlaymiz
    
    def __str__(self):
        return f'Attachment by {self.added_by.username} at {self.uploaded_at}'
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Kimga bildirishnoma 
    message = models.ForeignKey(Message, on_delete=models.CASCADE) # Qaysi xabarga bog'langan
    is_read = models.BooleanField(default=False) # O'qilganmi yoki yo'qmi 
    created_at = models.DateTimeField(auto_now_add=True) # Qachon yaratilgan
    
    def __str__(self):
        return f'Notification for {self.user.username} - Read: {self.is_read}'

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE) # Kimdan so'rov kelgan
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE) # Kimga so'rov kelgan
    created_at = models.DateTimeField(auto_now_add=True) # Qachon so'rov yuborilgan 
    
    class Meta:
        unique_together = ('from_user', 'to_user')
    
    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username}'
    
class Chat(models.Model):
    name = models.CharField(max_length=100) # Chat nomi
    creator = models.ForeignKey(User, on_delete=models.CASCADE) # Kim yaratgan
    members = models.ManyToManyField(User, related_name="chats") # Chat a'zolari
    created_at = models.DateTimeField(auto_now_add=True) # Qachon yaratilgan
    
    
    def __str__(self):
        return self.name