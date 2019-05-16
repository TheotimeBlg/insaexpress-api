"""insaexpress URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from api.views import PublicTeamsViewSet, TeamsViewSet, TeamAchievementsViewSet, AchievementsViewSet, LogoutViews, \
    CurrentUserViews, PositionUpdateViews


public_router = routers.DefaultRouter()
# Model to register a route : router.register(r'urlname', TheModelViewSet)
public_router.register(r'teams', PublicTeamsViewSet, base_name='public-teams')

router = routers.DefaultRouter()
# Model to register a route : router.register(r'urlname', TheModelViewSet)
router.register(r'teams', TeamsViewSet)
router.register(r'achievements', AchievementsViewSet)
router.register(r'team_achievements', TeamAchievementsViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^authenticate$', obtain_jwt_token),
    url(r'^authenticate/logout$', LogoutViews.as_view()),
    url(r'^', include(public_router.urls)),
    url(r'^manage/', include(router.urls)),
    url(r'^manage/me$', CurrentUserViews.as_view()),
    url(r'^update/$', PositionUpdateViews.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('upload/', include('uploadapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
