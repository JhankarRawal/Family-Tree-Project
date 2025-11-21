from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, login_view, logout_view, profile_view

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    

    # Password Reset URLs
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',          # form page
            email_template_name='accounts/password_reset_email.txt',  # text-only email
            subject_template_name='accounts/password_reset_subject.txt',
            success_url='/accounts/password-reset/done/'
        ),
        name='password_reset'
    ),
         
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),

 path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/password-reset-complete/'
        ),
        name='password_reset_confirm'
    ),

    # Password reset complete
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
