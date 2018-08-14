from django.urls import path
from django.conf.urls import url, include
from . import views, api
from django.contrib.auth.views import login, logout

from django.http import JsonResponse, HttpResponse

import os

urlpatterns = [
    url(r'^$', views.home),
    path(r'dashboard/', views.dashboard),
    path(r'dashboard/examp/', views.examp),
    path(r'dashboard/computer/<int:computer_id>', views.computer, name="computer"),
    path(r'dashboard/computer/<int:computer_id>/check-updates', views.computer_check_updates),
    path(r'dashboard/computer/<int:computer_id>/updates-in-progress', views.computer_updates_in_progress),
    path(r'dashboard/computer/<int:computer_id>/install-update/<int:update_id>', views.computer_install_update),
    path(r'dashboard/computer/search_log', views.search_log, name='search_log'),
    path(r'dashboard/alerts/', views.alerts, name='alerts'),
    path(r'dashboard/alerts/search', views.search, name='search'),
    path(r'logout/', logout),
    path(r'dashboard/alerts/approve/<int:alert_id>', views.approve_alert),
    url(r'^login/$', login, {'template_name': 'login.html'})

]
