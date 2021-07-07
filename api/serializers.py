from rest_framework import serializers

from api.models import User, Contact, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "phone_number", "name", "is_active"]


class ContactSerializer(serializers.ModelSerializer):
    is_registered = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Contact
        fields = "__all__"

    def get_is_registered(self, obj):
        return obj.is_registered


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
