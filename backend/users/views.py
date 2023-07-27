from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from utils.pagination import CustomPagination

from .models import Follow, User
from .serializers import FollowShowSerializer


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def follow(request, pk):
    user = get_object_or_404(User, username=request.user.username)
    following = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if user.id == following.id:
            return Response(
                'Нельзя подписаться на самого себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        elif Follow.objects.filter(user=user, following=following).exists():
            return Response(
                'Вы уже подписаны на этого пользователя',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(user=user, following=following)
        to_serializer = User.objects.filter(username=following)
        serializer = FollowShowSerializer(
            to_serializer,
            context={'request': request},
            many=True
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        try:
            subscription = Follow.objects.get(user=user, following=following)
        except ObjectDoesNotExist:
            return Response(
                'Вы не подписаны на этого пользователя',
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return HttpResponse(
            'Вы отписались от пользователя',
            status=status.HTTP_204_NO_CONTENT
        )


class FollowListViewsSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowShowSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
