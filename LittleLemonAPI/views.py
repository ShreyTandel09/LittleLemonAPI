from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from .permissions import IsManager,IsDeliveryCrew
from .models import MenuItem, Cart, Order, OrderItem, Category, CustomUser
from .serializers import MenuItemSerializer, CategorySerializer, ManagerListSerializer,CustomUserCreateSerializer,GroupSerializer,CustomUserSerializer,CartSerializer,CartAddSerializer,CartRemoveSerializer,OrderSerializer,SingleOrderSerializer,OrderPutSerializer
from .services import GroupService
import math
from datetime import date

# Create your views here.


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def manager_view(request):
#     # Check if the user is in the Manager group
#     try:
#         manager_group = Group.objects.get(name='Manager')
#     except Group.DoesNotExist:
#         return JsonResponse({'message': 'Manager group does not exist'}, status=404)

#     if request.user.groups.filter(name='Manager').exists():
#         # User is in the Manager group
#         return JsonResponse({'message': 'You have access to this view'})
#     else:
#         # User is not in the Manager group
#         return JsonResponse({'message': 'You do not have access to this view'}, status=403)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManager])
def manager_view(request):
    return JsonResponse({'message': 'You have permission to view this user.'}, status=status.HTTP_200_OK)

#User-list
class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    
    def get_queryset(self):
        # Get the group
        # Example: group = Group.objects.get(name='Admin')
        # Exclude superusers and users in the group
        # Example: return CustomUser.objects.exclude(is_superuser=True).exclude(groups=group)
        return CustomUser.objects.exclude(is_superuser=True)
    
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('id')
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                serializer = CustomUserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        queryset = self.get_queryset()
        serializer = CustomUserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
#Group
class CreateGroupView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        group_name = request.data.get('name')
        if group_name:
            # Check if the group already exists
            group = Group.objects.filter(name=group_name).first()
            if group:
                serializer = GroupSerializer(group)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # If the group doesn't exist, create it
            group = GroupService.create_group(group_name)
            serializer = GroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'Group name not provided'}, status=status.HTTP_400_BAD_REQUEST) 
    
    def get(self, request, *args, **kwargs):
        group_name = request.query_params.get('name')
        
        if group_name:
            # Check if the group already exists
            group = Group.objects.filter(name=group_name).first()
            if group:
                serializer = GroupSerializer(group)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If no specific group name is provided, return all groups
            groups = Group.objects.all()
            serializer = GroupSerializer(groups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    
# Category-list    
class CategoryView(generics.ListCreateAPIView):
    # throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        if self.request.method == "DELETE":
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return[permission() for permission in permission_classes]
        
    def patch(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({'message': f'Category updated successfully'}, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return JsonResponse({'message': f'Category deleted successfully'}, status=status.HTTP_200_OK)

# Menu-item-list
class MenuItemListView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()

    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        menuItem = self.get_object()
        serializer = self.get_serializer(menuItem, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({'message': f'Menu item updated successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        menuItem = self.get_object()
        menuItem.delete()
        return JsonResponse({'message': f'Menu item deleted successfully'}, status=status.HTTP_200_OK)

# Manager-list
class ManagersListView(generics.ListCreateAPIView):
    # queryset = Group.objects.filter(name='Manager')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    
    def get_queryset(self):
        return Group.objects.get(name='Manager').user_set.all()
            
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if username:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                return JsonResponse({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(user)
            return JsonResponse({'message': 'User added to managers group'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'Username not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
class ManagersRemoveView(generics.DestroyAPIView):
    
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    # def get_queryset(self):
    #     crew = Group.objects.get(name='Manager')
    #     return crew.user_set.all()

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.remove(user)
            return JsonResponse({'message': 'User removed from managers group'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)


class DeliveryCrewListView(generics.ListCreateAPIView):
    # queryset = Group.objects.filter(groups__name='Delivery crew')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    
    def get_queryset(self):
        crew = Group.objects.get(name='Delivery crew')
        return crew.user_set.all()

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                return JsonResponse({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
            crew = Group.objects.get(name='Delivery crew')
            crew.user_set.add(user)
            return JsonResponse(status=201, data={'message':'User added to Delivery Crew group'})
        return JsonResponse({'message': 'Username not provided'}, status=status.HTTP_400_BAD_REQUEST)


class DeliveryCrewRemoveView(generics.DestroyAPIView):
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    def get_queryset(self):
        crew = Group.objects.get(name='Delivery crew')
        return crew.user_set.all()
    
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        crew = Group.objects.get(name='Delivery crew')
        crew.user_set.remove(user)
        return JsonResponse(status=201, data={'message':'User removed from the Delivery crew group'})
    
class CartOperationsView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        return cart
    
    def post(self, request, *arg, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menuitem_id=id)
        except:
            return JsonResponse(status=409, data={'message':'Item already in cart'})
        return JsonResponse(status=201, data={'message':'Item added to cart!'})
    
    def delete(self, request, *arg, **kwargs):
        if request.data['menuitem']:
            serialized_item = CartRemoveSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            menuitem = request.data['menuitem']
            cart = get_object_or_404(Cart, user=request.user, menuitem=menuitem )
            cart.delete()
            return JsonResponse(status=200, data={'message':'Item removed from cart'})
        else:
            Cart.objects.filter(user=request.user).delete()
            return JsonResponse(status=201, data={'message':'All Items removed from cart'})
        
class OrderOperationsView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=self.request.user)
        else:
            return Order.objects.filter(user=self.request.user)
    
    def get_permissions(self):    
        if self.request.method == 'GET' or 'POST' : 
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return[permission() for permission in permission_classes]

    def post(self, request, *args, **kwargs):

        cart_items = Cart.objects.filter(user=request.user)
        print("Cart items for user:", request.user.username)
        print(cart_items)
        if not cart_items:
            return JsonResponse(status=400, data={'message':'Cart is empty'})
        total = math.fsum(item.price for item in cart_items)
        print(total)
        order = Order.objects.create(user=request.user, status=False, total=total, date=date.today())
        for i in cart_items.values():
            menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
            orderitem = OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'])
            orderitem.save()
        cart_items.delete()
        return JsonResponse(status=201, data={'message':'Your order has been placed! Your order number is {}'.format(str(order.id))})


class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SingleOrderSerializer

    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user and self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsDeliveryCrew | IsManager | IsAdminUser]
        return[permission() for permission in permission_classes] 
    
    def get_queryset(self, *args, **kwargs):
            query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
            return query
    
    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return JsonResponse(status=200, data={'message':'Status of order #'+ str(order.id)+' changed to '+str(order.status)})
    
    def put(self, request, *args, **kwargs):
        serialized_item = OrderPutSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew'] 
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(CustomUser, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return JsonResponse(status=201, data={'message':str(crew.username)+' was assigned to order #'+str(order.id)})
    
    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return JsonResponse(status=200, data={'message':'Order #{} was deleted'.format(order_number)})