from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeDoneView,
    PasswordChangeView, PasswordResetCompleteView,
    PasswordResetConfirmView, PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'signup/', views.SignUp.as_view(), name='signup'
    ),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'auth/password_change/',
        PasswordChangeView.as_view(
            template_name='users/auth/password_change_form.html',
        ),
        name='password_change_form'
    ),
    path(
        'auth/password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/auth/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'auth/password_reset/',
        PasswordResetView.as_view(
            template_name='users/auth/password_reset_form.html'),
        name='password_reset_form'
    ),
    path(
        'auth/password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='users/auth/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'auth/reset/<slug:uidb64>/<slug:token>/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
        ),
        name='password_reset_confirm'
    ),
    path(
        'auth/reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
