from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from tasks.permissions import IsOwnerOrAdmin, IsOwner, CreateTaskPermission
from tasks.utils.pagination import TaskPagination
from .serializers import CommentSerializer, TaskSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Task, TaskComment
from django.shortcuts import get_object_or_404
from django.db.models import Q

class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated, CreateTaskPermission]
    pagination_class = TaskPagination

    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            tasks = Task.objects.all().order_by('-id')
        else:
            tasks = Task.objects.filter(user=request.user).order_by('-id')
        
        status_filter = request.query_params.get("status")
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        project_filter = request.query_params.get("project")
        if project_filter:
            tasks = tasks.filter(project__id=project_filter)
        priority_filter = request.query_params.get("priority")
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)

        search_filter = request.query_params.get("search")
        if search_filter:
            tasks = tasks.filter(
                Q(name__icontains=search_filter) |
                Q(description__icontains=search_filter) 
                # Q(comments__icontains=search_filter)
            )
        paginator = self.pagination_class()
        paginated_tasks = paginator.paginate_queryset(tasks, request)

        serializer = TaskSerializer(paginated_tasks, many=True)

        return paginator.get_paginated_response({
            "message": "Tasks fetched successfully",
            "tasks": serializer.data,
            "page_size": paginator.page_size,
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages
        })

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Task created", "task":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class CreateListTaskGenericView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Task.objects.all()
        else:
            return Task.objects.filter(user=user)

    def get_serializer_context(self):
        return {'request': self.request}


class RetriveUpdateDeleteTaskGenericView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

class RetriveUpdateTaskView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task)
        return Response({"task":serializer.data}, status=status.HTTP_200_OK)


    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Task Updated Successfully", "task":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        task.delete()
        return Response({"message":"Task Deleted Successfully",}, status=status.HTTP_200_OK)


class AddCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Comment Added Successfully", "comment":serializer.data}, status=status.HTTP_201_CREATED)

class ListUpdateCommentsView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, pk):
        comments = TaskComment.objects.filter(task__id=pk)
        if not (request.user.is_staff or request.user.is_superuser):
            comments = comments.filter(user=request.user)

        serializer = CommentSerializer(comments, many=True)
        return Response({"message":"All Comments of Task", "comments":serializer.data}, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        comment = get_object_or_404(TaskComment, id=pk)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment, data = request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Comment updated", "comment":serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        comment = get_object_or_404(TaskComment, id=pk)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response({"message":"Task Comment Deleted Successfully",}, status=status.HTTP_200_OK)



