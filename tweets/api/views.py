
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params

# Create your views here.
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        serializer = TweetSerializerForDetail(
            self.get_object(),
            context={'request': request}
        )
        return Response(serializer.data)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets,
                                     context={'request': request},
                                     many=True,)
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        Reload create method,
        because the default user as the current login user
        """
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        serializer = TweetSerializer(tweet, context={'request': request})
        return Response(serializer.data, status=201)

