from rest_framework import generics, status,filters
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .models import CustomUser, FriendRequest, UserProfile
from .serializers import LoginSerializer, FriendRequestSerializer, UserProfileSerializer
from .serializers import UserSerializer
from rest_framework.pagination import PageNumberPagination
from django.db import models
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
    
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        # Make a mutable copy of request.data
        data = request.data.copy()
        data['email'] = data['email'].lower()
        
        # Pass the modified data to the serializer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        user = CustomUser.objects.filter(email=email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class UserSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserSearchView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserSearchPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # print("queryset earlier", queryset)
        search_query = self.request.query_params.get('search', '')
        if search_query:
            # Exact email match
            # print("search_query", search_query)
            if '@' in search_query:
                queryset = queryset.filter(email__iexact=search_query)
            else:
                queryset = queryset.filter(
                    models.Q(first_name__icontains=search_query) |
                    models.Q(last_name__icontains=search_query)
                )
        # print("queryset", queryset)
        return queryset


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from_user = request.user
        to_user_id = request.data.get('to_user_id')
        to_user = CustomUser.objects.get(id=to_user_id)

        # Check if already friends
        if from_user.userprofile.friends.filter(id=to_user.id).exists():
            return Response({"detail": "Already friends"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if request already sent
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({"detail": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if limit of 3 requests per minute is exceeded
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        if FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago).count() >= 3:
            return Response({"detail": "Cannot send more than 3 friend requests in a minute"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Create friend request
        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

class RespondToFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        friend_request_id = request.data.get('friend_request_id')
        action = request.data.get('action')

        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id, to_user=request.user)
        except FriendRequest.DoesNotExist:
            return Response({"detail": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            friend_request.is_accepted = True
            friend_request.save()
            from_user = friend_request.from_user
            to_user = friend_request.to_user
            from_user.userprofile.friends.add(to_user)
            to_user.userprofile.friends.add(from_user)
            return Response({"detail": "Friend request accepted"}, status=status.HTTP_200_OK)
            # request.user.userprofile.add_friend(friend_request.from_user)
            # return Response({"detail": "Friend request accepted"}, status=status.HTTP_200_OK)

        elif action == 'reject':
            friend_request.is_rejected = True
            friend_request.save()
            return Response({"detail": "Friend request rejected"}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class FriendListView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        # return self.request.user.userprofile
        try:
            user_profile = self.request.user.userprofile
        except UserProfile.DoesNotExist:
            raise status.Http404("UserProfile does not exist")
        return user_profile

    def get(self, request, *args, **kwargs):
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data)

class PendingFriendRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, is_accepted=False, is_rejected=False)

