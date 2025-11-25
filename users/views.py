from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.permissions import IsOwnerOrAdmin
from .serializers import UserLoginSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrAdminMixin:
    def check_owner_or_admin(self, request, user_obj):
        # allow if request.user is same user or is staff/superuser
        if request.user.is_authenticated and (request.user.pk == user_obj.pk or request.user.is_staff):
            return True
        return False


class UserCreateViews(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserCreateGenericView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    

class UserDetailsView(APIView, IsOwnerOrAdminMixin):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request, pk):
        user = get_object_or_404(User, id=pk)
        if not self.check_owner_or_admin(request, user):
            return Response({"status":"error", "message": "You must be the owner or an admin to access this."}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        user = get_object_or_404(User, id=pk)
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else: 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailsGenericView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(username=username, password=password)
            if not user:
                # Using generics
                # from rest_framework.exceptions import AuthenticationFailed
                # raise AuthenticationFailed("Invalid username or password")
                return Response({"message":"Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
            if not user.is_active:
                return Response({"message":"User account is disabled"}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

