from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly

from projects.permissions import IsProjectOwner, CanCreateProject, CanUpdateDeleteProject
from projects.serializers import ProjectMemberAddSerializer, ProjectSerializer
from tasks.models import Task
from tasks.utils.pagination import TaskPagination
from .models import Project, ProjectMember
from django.db.models import Q, Prefetch

class ProjectListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, CanCreateProject]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    pagination_class = TaskPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Project.objects.all()
        # return Project.objects.filter(members__user=user).exclude(members__role ="viewer")
        return Project.objects.filter(members__user=user)


    # ⭐ Custom POST Response
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.save()

        return Response({
            "success": True,
            "message": "Project created successfully",
            "data": self.get_serializer(project).data
        }, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        print('queryset: ', queryset)
        role = request.query_params.get("role")
        if role:
            queryset = queryset.filter(project__id=role)

        search_filter = request.query_params.get("search")
        if search_filter:
            queryset = queryset.filter(
                Q(name__icontains=search_filter) |
                Q(description__icontains=search_filter) 
                # Q(comments__icontains=search_filter)
            )
        
        project_search = request.query_params.get("projectsearch")
        if project_search:
            queryset = queryset.filter(
                Q(name__icontains=project_search) |
                Q(description__icontains=project_search)
            )
            print("Filtered Projects:", queryset)
        paginator = self.pagination_class()
        paginated_projects = paginator.paginate_queryset(queryset, request)

        serializer = ProjectSerializer(paginated_projects, many=True, context={'request': request})

        return paginator.get_paginated_response({
            "message": "Projects fetched successfully",
            "projects": serializer.data,
            "page_size": paginator.page_size,
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages
        })

class ProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, CanUpdateDeleteProject]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(members__user=user)


class AddProjectMemberView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def post(self, request):
        serializer = ProjectMemberAddSerializer(data=request.data)

        if serializer.is_valid():
            # Prevent duplicates
            project = serializer.validated_data['project']
            user = serializer.validated_data['user']

            if ProjectMember.objects.filter(project=project, user=user).exists():
                return Response(
                    {"message": "User already added to project"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()
            return Response(
                {"message": "Member added successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ListProjectMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        project = get_object_or_404(Project, id=pk)

        # Prefetch tasks assigned to each user BUT only for this project.
        # NOTE: Task.user.related_name == 'assigned_tasks' in your Task model.
        members_qs = (
            ProjectMember.objects.filter(project=project)
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "user__assigned_tasks",                       # related_name on Task.user
                    queryset=Task.objects.filter(project=project).order_by('-created_at')[:10],# only tasks of this project
                    to_attr="project_tasks"                       # will be available as user.project_tasks
                )
            )
        )

        project_members = []
        for m in members_qs:
            user = m.user
            # get tasks prefetched for this user for the current project
            tasks_for_user = getattr(user, "project_tasks", [])

            project_members.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "job_role": (user.job_role.replace("_", " ").title() if user.job_role else None),
                "department": user.department,
                "designation": user.designation,
                "project_role": m.role,
                "joined_at": m.joined_at,
                "tasks": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "status": t.status,
                        "priority": t.priority,
                        "due_date": t.due_date,
                    } for t in tasks_for_user
                ],
                "tasks_count": len(tasks_for_user),
            })

        return Response(
            {
                "project_id": project.id,
                "members_count": len(project_members),
                "members": project_members
            },
            status=status.HTTP_200_OK
        )


class RemoveProjectMemberView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def delete(self, request, project_id, member_id):
        self.check_permissions(request)
        member = ProjectMember.objects.filter(
            user_id=member_id, 
            project_id=project_id
        ).first()        
        if member.user == request.user:
            return Response({"error":"You can not delete your self."}, status=status.HTTP_403_FORBIDDEN)
        if not member:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        
        member.delete()
        
        return Response(
            {"message": f"{member.user.username} removed successfully"},
            status=status.HTTP_200_OK
        )