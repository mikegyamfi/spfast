from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views
from .auth import authViews


urlpatterns = [
    path('', views.home, name="home"),
    path('services', views.services, name='services'),
    path('services/mtn', views.mtn, name='mtn'),
    path('services/airtel-tigo/', views.airtel_tigo, name='airtel-tigo'),
    path('services/mtn/', views.mtn, name='mtn'),
    path('history/airtel-tigo', views.history, name='history'),
    path('history/mtn', views.mtn_history, name="mtn-history"),
    path('verify_transaction/<str:reference>/', views.verify_transaction, name="verify_transaction"),

    path('import_thing', views.populate_custom_users_from_excel, name="import_users"),
    path('delete', views.delete_custom_users, name='delete'),


    path('mtn_admin', views.admin_mtn_history, name='mtn_admin'),
    path('at_admin', views.admin_at_history, name='at_admin'),
    path('mark_as_sent/<int:pk>', views.mark_as_sent, name='mark_as_sent'),
    path('at_mark_as_sent/<int:pk>', views.at_mark_as_sent, name='at_mark_as_sent'),

    path('pay_with_wallet/', views.pay_with_wallet, name='pay_with_wallet'),
    path('credit_user', views.credit_user, name='credit_user'),
    path('mtn_pay_with_wallet/', views.mtn_pay_with_wallet, name='mtn_pay_with_wallet'),
    path('topup-info', views.topup_info, name='topup-info'),
    path("request_successful/<str:reference>", views.request_successful, name='request_successful'),
    path('elevated/topup-list', views.topup_list, name="topup_list"),
    path('credit/<str:reference>', views.credit_user_from_list, name='credit'),
    path('at_complete/<int:pk>/<str:status>', views.at_mark_completed, name='at_complete'),
    path('mtn_complete/<int:pk>/<str:status>', views.mtn_mark_completed, name='mtn_complete'),

    path('login', authViews.login_page, name='login'),
    path('signup', authViews.sign_up, name='signup'),
    path('logout', authViews.logout_user, name="logout")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
