# analytics/middleware.py
from threading import local
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AnonymousUser

import logging

logger = logging.getLogger("analytics")



_thread_locals = local()

def get_current_user():
    """Get current user from thread local"""
    return getattr(_thread_locals, 'user', None)


class ActivityLogMiddleware:
    """Middleware to store current user in thread local for signal handlers"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize authenticators
        self.jwt_auth = JWTAuthentication()
        # If using Token auth instead, use:
        # self.token_auth = TokenAuthentication()
    
    def __call__(self, request):
        # Try to authenticate user from JWT/Token
        user = self._authenticate_user(request)
        
        # Store user in thread local
        _thread_locals.user = user
        
        # logger.info(f"Authenticated user {getattr(user, 'id', None)} {getattr(user, 'username', None)}")

        # Also attach to signal handlers
        from .signals import task_post_save, task_pre_delete, comment_post_save
        task_post_save.thread_local = _thread_locals
        task_pre_delete.thread_local = _thread_locals
        comment_post_save.thread_local = _thread_locals
        
        response = self.get_response(request)
        
        # Clean up
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        
        return response
    
    def _authenticate_user(self, request):
        """Authenticate user from JWT token or fallback to request.user"""
        
        # Skip authentication for non-API requests (like admin)
        if not request.path.startswith('/api/'):
            return getattr(request, 'user', None)
        
        # Try JWT authentication
        try:
            auth_result = self.jwt_auth.authenticate(request)
            if auth_result is not None:
                user, token = auth_result
                return user
        except Exception as e:
            logger.error(f"JWT auth failed: {e}")
            pass
        
        # If using Token authentication, uncomment this:
        # try:
        #     auth_result = self.token_auth.authenticate(request)
        #     if auth_result is not None:
        #         user, token = auth_result
        #         return user
        # except Exception:
        #     pass
        
        # Fallback to request.user (for session auth, admin)
        return getattr(request, 'user', None)


# Alternative: Simpler version that just gets user from request
# Use this if you don't want to duplicate authentication logic
class SimpleActivityLogMiddleware:
    """Simpler middleware - just passes through request.user"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Called after URL is resolved but before view is called"""
        # At this point, authentication hasn't happened yet
        # So we can't get the authenticated user here either
        return None
    
    def __call__(self, request):
        response = self.get_response(request)
        return response