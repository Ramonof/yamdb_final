import csv
import io
import random

from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Comment, Review
from titles.filters import TitleFilter
from titles.models import Category, Genre, Title
from users.models import User

from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrAdminOrModerator
from .serializers import (
    CategorySerializer, CheckConfirmationCodeSerializer, CommentSerializer,
    GenreSerializer, ReviewSerializer, SendCodeSerializer,
    TitleCreateSerializer, TitleListSerializer, UserSerializer)


@api_view(['POST'])
def send_confirmation_code(request):
    serializer = SendCodeSerializer(data=request.data)
    email = request.data['email']
    serializer.is_valid(raise_exception=True)
    confirmation_code = ''.join(map(str, random.sample(range(10), 6)))
    user = User.objects.filter(email=email).exists()
    if not user:
        User.objects.create_user(email=email)
    User.objects.filter(email=email).update(
        confirmation_code=make_password(
            confirmation_code,
            salt=None,
            hasher='default'
        )
    )
    mail_subject = 'Код подтверждения на Yamdb.ru'
    message = f'Ваш код подтверждения: {confirmation_code}'
    send_mail(mail_subject, message, 'Yamdb.ru <admin@yamdb.ru>', [email])
    return Response(
        f'Код отправлен на адрес {email}', status=status.HTTP_200_OK
    )


@api_view(['POST'])
def get_jwt_token(request):
    serializer = CheckConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    confirmation_code = serializer.data.get('confirmation_code')
    user = get_object_or_404(User, email=email)
    if check_password(confirmation_code, user.confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def user_csv_update(request):
    if not request.user.is_authenticated:
        return Response(
            'Вы не авторизованы', status=status.HTTP_401_UNAUTHORIZED
        )
    if not User.is_admin(request.user):
        return Response(
            'У вас не хватает прав', status=status.HTTP_401_UNAUTHORIZED
        )
    csv_file = request.data.get('file')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = User.objects.update_or_create(
            id=column[0],
            username=column[1],
            email=column[2],
            role=column[3],
            bio=column[4],
            first_name=column[5],
            last_name=column[6]
        )
        return Response(status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if self.request.method in SAFE_METHODS:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class LCDViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    pass


class CategoryViewSet(LCDViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'


class GenreViewSet(LCDViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleListSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrAdminOrModerator]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        return self.queryset.filter(title_id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrAdminOrModerator]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(review_id=self.kwargs['review_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
