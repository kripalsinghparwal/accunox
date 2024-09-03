from rest_framework import serializers
from .models import CustomUser, FriendRequest, UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'].lower(),
            password=validated_data['password'],
        )
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name']


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'is_accepted', 'is_rejected', 'timestamp']

# class FriendListSerializer(serializers.ModelSerializer):
#     friends = UserSerializer(many=True)

#     class Meta:
#         model = UserProfile
#         fields = ['friends']
class UserProfileSerializer(serializers.ModelSerializer):
    friends = UserSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['friends']

