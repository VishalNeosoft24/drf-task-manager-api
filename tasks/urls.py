from django.urls import path
from . import views

urlpatterns = [
    path("", view=views.CreateTaskView.as_view(), name="create_task"),
    path("<int:pk>/", view=views.RetriveUpdateTaskView.as_view(), name="retrive_update"),
    path("comment/", view=views.AddCommentView.as_view(), name="add_comment"),
    path("comment/<int:pk>/", view=views.ListUpdateCommentsView.as_view(), name="list_update_comment"),
]
