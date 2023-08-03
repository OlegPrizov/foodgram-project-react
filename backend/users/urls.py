from django.urls import include, path

from users.views import FollowListView, FollowView

app_name = 'users'

urlpatterns = [
    path('users/<int:id>/subscribe/', FollowView.as_view(), name='subscribe'),
    path(
        'users/subscriptions/',
        FollowListView.as_view(),
        name='subscriptions'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
