"""
URL configuration for intern_score_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
# intern_score_manager/urls.py
from django.contrib import admin
from django.urls import path
from score_app import views  # Import from score_app directly, not with the project name

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('display/loc', views.display, name='display'),
    path('display/luu', views.save, name='save'),
    path('display/', views.display_excel, name='display_excel'),
    path('update/', views.update_row, name='update_row'),
]
