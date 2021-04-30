from django.conf.urls import url, include
from leave_management.views import LeaveApplicationView


from rest_framework.routers import DefaultRouter


urlpatterns = [
    url('', LeaveApplicationView.as_view())

]