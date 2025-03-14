"""
URL configuration for suhyun_nlp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings #요거
from django.conf.urls.static import static #이 두줄과
from . import views

urlpatterns = [
    path("admin/", admin.site.urls, name='to-admin'),
    path('', views.to_index, name='to-index'),
    path('login/', views.to_login, name='to-login'),
    path('logout/', views.to_logout, name='to-logout'),
    path('signup/', views.to_signup, name='to-signup'),
    path('write/', views.to_write, name='to-write'),
    path('main/', views.to_main, name='to-main'),
    path('read/', views.to_read, name='to-read'),
    path('genre_management/', views.to_genre_management, name='to-genremanagement'),
    path('add_genre/', views.to_add_genre, name='to-add-genre'),
    path('delete_genre/', views.to_delete_genre, name='to-delete-genre'),
    path('detail/<int:id>/', views.to_detail, name='to-detail'),
    path('collaborate/<int:id>/', views.to_collaborate, name='to-collaborate'),
    path('inprogress/', views.to_inprogress, name='to-inprogress'),
]
