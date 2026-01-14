import logging
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from tasks.permissions import IsOwnerOrAdmin, IsOwner, CreateTaskPermission
from tasks.utils.pagination import TaskPagination
from tasks.utils.search_tasks_func import bump_task_search_version
from tasks.utils.task_filters import apply_task_filters, get_base_tasks_queryset
from .serializers import CommentSerializer, TaskSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Task, TaskComment
from django.shortcuts import get_object_or_404

class CreateTaskView(APIView):
    """
    API view to create a new task and list tasks with filtering and pagination.
    1. GET method:
       - Retrieves a list of tasks based on the user's role (admin or regular user).
       - Applies filters from query parameters (status, project, priority, search).
       - Orders tasks by descending ID.
       - Paginates the results using TaskPagination.
       - Returns a paginated response with task data and pagination details.
    2. POST method:
       - Accepts task data to create a new task.
       - Validates the input data using TaskSerializer.
       - Saves the new task if the data is valid.
       - Invalidates the task search cache by incrementing the "task_search_version" in the cache.
       - Returns a success response with the created task data or error details if validation fails.
    """
    permission_classes = [IsAuthenticated, CreateTaskPermission]
    pagination_class = TaskPagination

    def get(self, request):
        """
        Docstring for get
        
        :param self: Description
        :param request: Description
        """
        # Base queryset
        tasks = get_base_tasks_queryset(request.user)

        # Apply filters
        tasks = apply_task_filters(tasks, request.query_params)

        # Ordering
        tasks = tasks.order_by("-id")

        paginator = self.pagination_class()
        paginated_tasks = paginator.paginate_queryset(tasks, request)

        serializer = TaskSerializer(paginated_tasks, many=True)

        return paginator.get_paginated_response({
            "message": "Tasks fetched successfully",
            "tasks": serializer.data,
            "page_size": paginator.page_size,
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
        })

    def post(self, request):
        """
        Docstring for post
        
        :param self: Description
        :param request: Description
        """
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Invalidate search cache
            bump_task_search_version()
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
    """
    API view to retrieve, update, or delete a specific task by its ID.
    
    2. PATCH method:
       - Updates the task with the specified ID using partial data.
       - Validates the input data using TaskSerializer.
       - Saves the updated task if the data is valid.
       - Invalidates the task search cache by incrementing the "task_search_version" in the cache.
       - Returns a success response with the updated task data or error details if validation fails.
    3. DELETE method:
       - Deletes the task with the specified ID.
       - Checks if the requesting user has permission to delete the task.
       - Invalidates the task search cache by incrementing the "task_search_version" in the cache.
       - Returns a success response upon successful deletion.       
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def get(self, request, pk):
        """
        Docstring for get
        
        :param self: Description
        :param request: Description
        :param pk: Description
        """
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task, context={'request': request})
        return Response({"task":serializer.data}, status=status.HTTP_200_OK)


    def patch(self, request, pk):
        """
        Docstring for patch
        
        :param self: Description
        :param request: Description
        :param pk: Description
        """
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            # Invalidate search cache
            bump_task_search_version()
            return Response({"message":"Task Updated Successfully", "task":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Docstring for delete
        
        :param self: Description
        :param request: Description
        :param pk: Description
        """
        task = get_object_or_404(Task, id=pk)
        self.check_object_permissions(request, task)
        task.delete()
        # Invalidate search cache
        bump_task_search_version()
        return Response({"message":"Task Deleted Successfully",}, status=status.HTTP_200_OK)


class AddCommentView(APIView):
    """
    API view to add a comment to a specific task.
    1. POST method:
       - Accepts comment data to create a new comment for a task.
       - Validates the input data using CommentSerializer.
       - Saves the new comment if the data is valid.
       - Returns a success response with the created comment data or error details if validation fails.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Docstring for post
        
        :param self: Description
        :param request: Description
        """
        serializer = CommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Comment Added Successfully", "comment":serializer.data}, status=status.HTTP_201_CREATED)

class ListUpdateCommentsView(APIView):
    """
    Docstring for ListUpdateCommentsView
    API view to list all comments for a specific task and update or delete a specific comment.
    1. GET method:
       - Retrieves all comments associated with the task identified by the provided ID.
       - If the requesting user is not an admin, filters comments to only include those made by the user.
       - Serializes the comments using CommentSerializer.
       - Returns a success response with the serialized comment data.
    2. PATCH method:
       - Updates a specific comment identified by its ID.
       - Checks if the requesting user has permission to update the comment.
       - Validates the input data using CommentSerializer.
       - Saves the updated comment if the data is valid.
       - Returns a success response with the updated comment data or error details if validation fails.
    3. DELETE method:
       - Deletes a specific comment identified by its ID.
       - Checks if the requesting user has permission to delete the comment.
       - Returns a success response upon successful deletion."""
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, pk):
        """
        Docstring for get
        
        :param self: Description
        :param request: Description
        :param pk: Description
        """
        comments = TaskComment.objects.filter(task__id=pk)
        if not (request.user.is_staff or request.user.is_superuser):
            comments = comments.filter(user=request.user)

        serializer = CommentSerializer(comments, many=True)
        return Response({"message":"All Comments of Task", "comments":serializer.data}, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        """
        Docstring for patch
        
        :param self: Description
        :param request: Description
        :param pk: Description
        """
        comment = get_object_or_404(TaskComment, id=pk)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment, data = request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Comment updated", "comment":serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Docstring for delete
        
        :param self: Description
        :param request: Description
        :param pk: Description
        """
        comment = get_object_or_404(TaskComment, id=pk)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response({"message":"Task Comment Deleted Successfully",}, status=status.HTTP_200_OK)



