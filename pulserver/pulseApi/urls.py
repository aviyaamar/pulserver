from django.urls import path
from . import views


urlpatterns = [
    path('statistics/<str:auth_key>/<str:computer_auth>', views.process_statistics),
    path('register/<str:auth_key>', views.register_comp),
    path('command_results/<str:auth_key>/<str:computer_auth>', views.process_commands),
    path('query_commands/<str:auth_key>/<str:computer_auth>', views.query_commands),
]
