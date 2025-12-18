from django.contrib import admin
from django.urls import path, include
from loggerapp import views as log_views
from django.contrib.auth import views as auth_views
from loggerapp.forms import CustomPasswordResetForm
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', log_views.home, name='home'),
    path('signup/', log_views.signup, name='signup'),
    path('login/', log_views.login_view, name='login'),
    path('logout/', log_views.logout_view, name='logout'),
    path('history/', log_views.history, name='history'),
    path('graph/', log_views.graph, name='graph'),
    path('about/', log_views.about, name='about'),
    path('export/', log_views.export_csv, name='export_csv'),
    path('terms/', log_views.terms, name='terms'),
    path('', include('loggerapp.urls')), 
    path("password_reset/", auth_views.PasswordResetView.as_view(
        form_class=CustomPasswordResetForm,
        template_name="password/password_reset.html",
        email_template_name="password/password_reset_email.html",
        success_url="/password_reset_done/"
    ), name="password_reset"),
    
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view( #User ID in a special encoded form(uidb64) and A secret code that proves the link is valid(token)
        template_name='password/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password/password_reset_complete.html'
    ), name='password_reset_complete'),
]
