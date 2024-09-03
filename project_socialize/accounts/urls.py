from django.urls import path
from .views import RegisterView, LoginView
from .views import UserSearchView, SendFriendRequestView, RespondToFriendRequestView, FriendListView, PendingFriendRequestsView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user_search'),
    path('search/', UserSearchView.as_view(), name='user_search'),
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friend-request/respond/', RespondToFriendRequestView.as_view(), name='respond_friend_request'),
    path('friends/', FriendListView.as_view(), name='friends_list'),
    path('friend-requests/pending/', PendingFriendRequestsView.as_view(), name='pending_friend_requests'),
]

urlpatterns += [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]