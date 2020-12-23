from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User


class SendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class CheckConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role',
        )
        model = User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


# добавляем произведение
class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True,
        queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        fields = (
            'id', 'name',
            'year', 'genre',
            'category', 'description')
        model = Title


# возвращаем список произведений
class TitleListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'category', 'genre', 'rating',)
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        attrs['title'] = get_object_or_404(Title,
                                           id=self.context['view'].kwargs[
                                               'title_id'])
        if not self.partial and Review.objects.filter(
                title=attrs['title'],
                author=self.context[
                    'request'].user).exists():
            raise ValidationError(
                {'author': 'Вы уже оставляли отзыв на это произведение'})
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')

    def validate(self, attrs):
        attrs['review'] = get_object_or_404(Review,
                                            id=self.context['view'].kwargs[
                                                'review_id'],
                                            title_id=
                                            self.context['view'].kwargs[
                                                'title_id'])
        return attrs
