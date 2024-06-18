from rest_framework import permissions
from django.contrib.auth.models import Group

from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Delivery crew').exists()
    
    
# from rest_framework.permissions import IsAuthenticated, IsAdminUser

# class YourViewClassName(APIView):
#     def get_permissions(self):
#         permission_classes = [IsAuthenticated]
#         if self.request.method != 'GET':
#             permission_classes.append(IsAdminUser)
#         return [permission() for permission in permission_classes]

#     def get(self, request, *args, **kwargs):
#         # Your GET method logic here
#         pass

#     def post(self, request, *args, **kwargs):
#         # Your POST method logic here
#         pass

#     # Define other HTTP methods as needed
