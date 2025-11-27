from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from projects.permissions import IsProjectOwner
from projects.serializers import ProjectMemberAddSerializer, ProjectSerializer
from .models import Project, ProjectMember

class ProjectListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(members__user=user)



class ProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
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
        members = ProjectMember.objects.filter(project=project).select_related("user")

        project_members = [
            {
                "id": m.user.id,
                "username": m.user.username,
                "email": m.user.email,
                "role": m.user.role,
                "department": m.user.department,
                "designation": m.user.designation
            } for m in members
        ]

        return Response(
            {"project_id": project.id, "members": project_members},
            status=status.HTTP_200_OK
        )


class RemoveProjectMemberView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def delete(self, request, member_id):
        member = get_object_or_404(ProjectMember, id=member_id)

        # Check permission dynamically
        self.check_object_permissions(request, member.project)

        member.delete()

        return Response(
            {"message": "Project member removed successfully"},
            status=status.HTTP_200_OK
        )