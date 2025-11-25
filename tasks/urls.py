from django.urls import path
from . import views

urlpatterns = [
    path("", view=views.CreateTaskView.as_view(), name="create_task"),
    path("<int:pk>/", view=views.RetriveUpdateTaskView.as_view(), name="retrive_update")
]
