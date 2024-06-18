from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import CustomUser, MenuItem, Cart, Category, Order, OrderItem

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
        }

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
        }
        
class CustomUserSerializer(UserSerializer):
    groups = serializers.StringRelatedField(many=True) 

    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'groups')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        depth = 1

class ManagerListSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True) 
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'groups')
  
 #Cart-Serailizers 
        
#Helper to handle the foregin key Constratint        
class CartHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price']
        
                
class CartSerializer(serializers.ModelSerializer):
    menuitem = CartHelpSerializer()
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'user', 'quantity']
        
class CartAddSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem','quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }
class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem']
        

class OrderSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    class Meta():
        model = Order
        fields = ['id','user','total','status','delivery_crew','date']
        
class SingleHelperSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['title','price']
        

                
class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = SingleHelperSerializer()
    class Meta():
        model = OrderItem
        fields = ['menuitem','quantity']
        
                
class OrderPutSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['delivery_crew']