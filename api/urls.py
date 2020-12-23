from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, get_jwt_token,
                    send_confirmation_code, user_csv_update)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register('titles/(?P<title_id>[^/.]+)/reviews', ReviewViewSet,
                basename='review')
router.register(
    'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments',
    CommentViewSet,
    basename='comment')


auth_patterns = [
    path('email/', send_confirmation_code, name='get_token'),
    path('token/', get_jwt_token, name='send_confirmation_code'),
]

urlpatterns = [
    path('v1/auth/', include(auth_patterns)),
    path('v1/update/users/', user_csv_update, name='update_database_users'),
    path('v1/', include(router.urls)),
]
