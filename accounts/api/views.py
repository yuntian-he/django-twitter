from accounts.api.serializers import (
    UserSerializer,
    SignupSerializer,
    LoginSerializer,
    UserSerializerWithProfile,
    UserProfileSerializerForUpdate,
)
from accounts.models import UserProfile
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from utils.permissions import IsAuthenticated


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    permission_classes = (permissions.IsAdminUser,)


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny, )
    serializer_class = SignupSerializer

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """
        user username, email, password to signup
        """
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        user = serializer.save()
        user.profile
        django_login(request, user)

        return Response({'success': True,
                         'user': UserSerializer(user).data,
                         }, status = 201)

    @action(methods=['POST'], detail=False)
    def login(self, request):
        """
        username: admin
        password: admin
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does not match",
            }, status=400)
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        check current user's status and detail information
        """
        data = {
            'has_logged_in': request.user.is_authenticated,
            }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """
        log out current user
        """
        django_logout(request)
        return Response({"success": True})


class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializerForUpdate