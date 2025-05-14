from rest_framework import serializers
from .models import User, Message, Profile, Attachment, Notification, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        
        

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True) # Senderni faqat o'qish uchun
    
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']
        read_only_fields = ['timestamp'] # timestamp faqat o'qish uchun
        
        
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Userni faqat o'qish uchun
    
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'age', 'image', 'bio']
        read_only_fields = ['user']
        
        
class AttachmentSerializer(serializers.ModelSerializer):
    message = MessageSerializer(read_only=True) # Messageni faqat o'qish uchun
    added_by = UserSerializer(read_only=True) # Kim yuklaganini faqat o'qish uchun
    
    
    class Meta:
        model = Attachment
        fields = ['id', 'message', 'file', 'uploaded_at', 'added_by']
        read_only_fields = ['uploaded_at', 'added_by']
        
        
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Kimga bildirishnomaligini faqat o'qish uchun
    message = MessageSerializer(read_only=True) # Qaysi xabarga bog'langanligini faqat o'qish uchun
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True) # Qachon yaratilganligini faqat o'qish uchun
    is_read = serializers.BooloeanField(default=False) # O'qilganmi yo'qmi tekshirish uchun
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['created_at', 'user', 'message']
        

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True) # Kimdan so'rov kelganini faqat o'qish uchun
    to_user = UserSerializer(read_only=True) # Kimga so'rov kelganini faqat o'qish uchun
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True) # Qachon so'rov yuborilganligini faqat o'qish uchun
     
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'created_at']
        read_only_fields = ['created_at', 'from_user', 'to_user']
        

    
    
    
    
    