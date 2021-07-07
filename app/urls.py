from django.conf.urls import url

from app import views

urlpatterns = [
    url(r'getTableData/', views.getTableData),
    url(r'getAllCount/', views.getAllCount),
    url(r'getMyInfo/', views.getMyInfo),
    url(r'getPermission/', views.getPermission),
    url(r'getPermissionData/', views.getPermissionData),

    url(r'register/', views.register),
    url(r'login/', views.login),
    url(r'logOut/', views.logOut),
    url(r'loginCheck/', views.loginCheck),
    url(r'getPredictData/', views.getPredictData),
    url(r'downloadPredictCSV/', views.downloadPredictCSV),

    url(r'postFormData/', views.postFormData),
    url(r'postPermissionData/', views.postPermissionData),
    url(r'delUserInfo/', views.delUserInfo),
]
