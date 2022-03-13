"""SCSapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from SCSapp import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin', admin.site.urls),

    path('login', views.logInUserView, name='login'),
    path('signup', views.signUpUserView, name='signup'),
    path('logout', views.logoutUser, name="logout"),

    path('', views.compHomePageView, name='homePage'),
    path('past', views.pastCompetitionsView, name='pastCompetition' ),
    path('createCompetition', views.createCompetitionsView, name='createCompetition'),
    path('competition/<comp_id>', views.competitionView, name='competition'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)