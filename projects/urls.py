from django.urls import path
from . import views


urlpatterns = [
    path("", view=views.ProjectListCreateView.as_view(), name='list_create_project'),
    path("<int:pk>/", view=views.ProjectRetrieveUpdateDestroyView.as_view(), name='project_detail'),
    path("member/add/", view=views.AddProjectMemberView.as_view(), name="add_project_member"),
    path("<int:pk>/members/", view=views.ListProjectMembersView.as_view(), name="list_project_members"),
    path('<int:project_id>/members/<int:member_id>/remove/', views.RemoveProjectMemberView.as_view(), name='project_member_remove'),
]
