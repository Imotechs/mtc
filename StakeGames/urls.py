
from django.contrib import admin
from django.urls import path,include,reverse_lazy
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('stakes/12/23/41_admin/', admin.site.urls),
    path('',include('mainapp.urls')),
    path('met/admin/',include('dashboard.urls')),
    path('users/',include('users.urls')),
    # path('games/',include('games.urls')),
    path('logout/',auth_views.LogoutView.as_view(),name = 'logout'),
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            success_url = reverse_lazy('password_reset_done'),
            template_name = 'mainapp/password_reset.html'),
            name = 'password_reset'),

    path('password-reset-done/', 
        auth_views.PasswordResetDoneView.as_view(template_name = 'mainapp/password_reset_done.html'),name = 'password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            success_url = reverse_lazy('password_reset_complete'),
            template_name = 'mainapp/password_reset_confirm.html'),
            name = 'password_reset_confirm'),
    
    path('password_reset_complete/', 
        auth_views.PasswordResetCompleteView.as_view( template_name = 'mainapp/password_reset_complete.html'), name = 'password_reset_complete'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
