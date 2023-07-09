from django.shortcuts import render
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework import mixins
from recepies.models import Follow
from api.serializers import FollowSerializer

class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet    
    ):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.follower.all()

