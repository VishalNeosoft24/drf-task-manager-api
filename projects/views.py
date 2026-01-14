from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from projects.permissions import IsProjectOwner, CanCreateProject, CanUpdateDeleteProject
from projects.permissions_constant.permission_utils import get_user_permissions
from projects.serializers import ProjectMemberAddSerializer, ProjectSerializer
from tasks.models import Task
from .utils.pagination import ProjectPagination
from .models import Project, ProjectMember
from django.db.models import Q, Prefetch, F, Max, Case, When, IntegerField, Value, Prefetch
from django.db.models.functions import Coalesce


class ProjectListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, CanCreateProject]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    pagination_class = ProjectPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            qs = Project.objects.all()
        else:
            # qs = Project.objects.filter(members__user=user).exclude(members__role ="viewer")
            qs = Project.objects.filter(members__user=user)

        qs = qs.annotate(
            last_activity=Coalesce(
                Max("tasks__updated_at"),
                F("updated_at"),
                F("created_at")
            )
        ).order_by('-last_activity')
        return qs

    # Custom POST Response
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
        
        role_filter = request.query_params.get("role_filter")
        if role_filter:
            queryset = queryset.filter(members__role=role_filter, members__user=request.user) 

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
    
    def retrieve(self, request, *args, **kwargs):
            project = self.get_object()   # DRF handles 404 safely
            serializer = self.get_serializer(project)
            project_summary = None

            # 🔥 Get dynamic permissions for the requesting user
            perms = get_user_permissions(request.user, project)

            if request.user.is_staff or request.user.is_superuser  or request.user.role in ["owner", "admin"]:
                project_tasks_summary = Task.objects.filter(project_id=project.id)
                user_task_summary = Task.objects.filter(project_id=project.id, user=request.user)

                project_summary = {
                    "total_tasks": project_tasks_summary.count(),
                    "todo_tasks": project_tasks_summary.filter(status="todo").count(),
                    "in_progress_tasks": project_tasks_summary.filter(status="progress").count(),
                    "completed_tasks": project_tasks_summary.filter(status="done").count(),
                }

            else:
                user_task_summary = Task.objects.filter(user=request.user, project_id=project.id)

            user_summary = {
                "total_tasks": user_task_summary.count(),
                "todo_tasks": user_task_summary.filter(status="todo").count(),
                "in_progress_tasks": user_task_summary.filter(status="progress").count(),
                "completed_tasks": user_task_summary.filter(status="done").count(),
            }

            # Merge the data with custom permissions
            data = serializer.data
            data["permissions"] = perms
            data["summary"] = {
                    "project_summary": project_summary,
                    "user_summary": user_summary
                }
            return Response(data)


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

        # Fetch ONLY members

        # members_qs = (
        #     ProjectMember.objects.filter(project=project)
        #     .select_related("user")
        #     .prefetch_related(
        #         Prefetch(
        #             "user__assigned_tasks",
        #             queryset=Task.objects.filter(project=project).order_by('-created_at')[:10],
        #             to_attr="project_tasks"
        #         )
        #     )
        # )

        # Order requesting user first
        members_qs = (
            ProjectMember.objects
            .filter(project=project)
            .select_related("user")
            .annotate(
                is_me=Case(
                    When(user=request.user, then=Value(0)),  # requested user first
                    default=Value(1),
                    output_field=IntegerField()
                )
            )
            .order_by("is_me", "joined_at")  # keep stable order
            .prefetch_related(
                Prefetch(
                    "user__assigned_tasks",
                    queryset=Task.objects.filter(project=project, status__in=["todo", "progress"]).order_by("-created_at")[:10],
                    to_attr="project_tasks"
                )
            )
        )

        # Fetch tasks created by users NOT in members list (superadmins/staff)
        member_user_ids = members_qs.values_list("user_id", flat=True)

        system_tasks = Task.objects.filter(project=project).exclude(user_id__in=member_user_ids)

        # Build members list
        project_members = []
        for m in members_qs:
            user = m.user
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

        # Return superadmin tasks in a separate key
        system_tasks_list = [
            {
                "id": t.id,
                "name": t.name,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date,
                "created_by": t.user.username,
            }
            for t in system_tasks
        ]

        return Response(
            {
                "project_id": project.id,
                "members_count": len(project_members),
                "members": project_members,
                "system_tasks_count": len(system_tasks_list),
                "system_tasks": system_tasks_list,
            }, status=200
        )


class RemoveProjectMemberView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def delete(self, request, project_id, member_id):
        self.check_permissions(request)
        member = ProjectMember.objects.filter(
            user_id=member_id, 
            project_id=project_id
        ).first() 
        if member is None:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)       
        if member.user == request.user:
            return Response({"error":"You can not delete your self."}, status=status.HTTP_403_FORBIDDEN)
        if not member:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        
        member.delete()
        
        return Response(
            {"message": f"{member.user.username} removed successfully"},
            status=status.HTTP_200_OK
        )