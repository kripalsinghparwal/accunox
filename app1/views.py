from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from django.db.models import Q
from rest_framework.throttling import UserRateThrottle

User = get_user_model()

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '').lower()
        return User.objects.filter(
            Q(email__iexact=query) | 
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct()

    def paginate_queryset(self, queryset, view=None):
        return super().paginate_queryset(queryset, view=view)

class FriendRequestThrottle(UserRateThrottle):
    rate = '3/min'

class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [FriendRequestThrottle]

    def post(self, request, *args, **kwargs):
        receiver = User.objects.get(id=request.data['receiver_id'])
        friend_request, created = FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
        if not created:
            return Response({'message': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Friend request sent.'}, status=status.HTTP_201_CREATED)

class RespondFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        friend_request = FriendRequest.objects.get(id=kwargs['pk'], receiver=request.user)
        friend_request.status = request.data['status']
        friend_request.save()
        return Response({'message': 'Friend request status updated.'})

class ListFriendsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        friends = User.objects.filter(
            Q(sent_requests__receiver=self.request.user, sent_requests__status='accepted') |
            Q(received_requests__sender=self.request.user, received_requests__status='accepted')
        ).distinct()
        return friends

class ListPendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status='pending')
