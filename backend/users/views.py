from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.pagination import CustomPagination

from .models import Follow, User
from .serializers import FollowSerializer, FollowShowSerializer


class FollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        serializer = FollowSerializer(
            data={'user': request.user.id, 'following': id},
            context={'request': request}
        )
        print(self.request.user)
        print(User.objects.get(id=id))
        if serializer.is_valid():
            serializer.save()
            print(Follow.objects.all())
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, requets, id):
        follow = get_object_or_404(Follow)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListView(ListAPIView):
    serializer_class = FollowShowSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
