from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from reviews.models import Category, Genre, Title
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, viewsets, status
from rest_framework.permissions import ( IsAuthenticated)
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from .mixins import CreateListDestroyViewSet
from .permissions import IsAdminOrReadOnly, IsAdministrator
from rest_framework.response import Response
from .serializers import CategorySerializer, GenreSerializer, RegisterSerializer, TitleSerializer, \
    OnlyReadTitleSerializer, MyTokenObtainPairSerializer, UserSerializer

User = get_user_model()


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg("reviews__score")
    ).order_by("name")
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category', 'genre', 'name', 'year')

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return OnlyReadTitleSerializer
        return TitleSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def Token(request):
    serializer = MyTokenObtainPairSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = get_object_or_404(User, username=serializer.validated_data.get("username"))
        access = AccessToken.for_user(user)
        return Response(f'token: {access}', status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = RegisterSerializer(data=request.data)
    if User.objects.filter(username=request.data.get("username"),
                           email = request.data.get("email")).exists():
        user, created = User.objects.get_or_create(username=request.data.get("username"))
        if created is False:
            confirmation_code = default_token_generator.make_token(user)
            user.confirmation_code = confirmation_code
            user.save()
            return Response("Обновление токена", status= status.HTTP_200_OK)
    serializer.is_valid(raise_exception=True)
    serializer.save()


    user = User.objects.get(username=request.data["username"], email=request.data["email"])
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    send_mail(
        subject="Регистрация в проекте YaMDb",
        message=f"Ваш проверочный код: {confirmation_code}",
        from_email="pahkarus@gmail.com",
        recipient_list=[user.email],
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [filters.SearchFilter]

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        if 'role' in request.data:
            return Response(serializer.data,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data)
