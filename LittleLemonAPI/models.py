# your_app/models.py
from django.contrib.auth.models import AbstractUser,User
from django.db import models
from datetime import date

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    
    def __str__(self):
        return self.username


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)
    
    class Meta:
        unique_together = [['slug', 'title']]

    def __str__(self):
        return self.title
        # return f"Category( title={self.title}, slug={self.slug})"
    
    
class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
        
    def __str__(self):
        # return f"MenuItem( title={self.title}, price={self.price},featured={self.featured},category={self.category})"
        return self.title

    
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('menuitem', 'user')

    def __str__(self):
        # return self.user.username
        return f"Cart(user={self.user.username}, menuitem={self.menuitem.title}, quantity={self.quantity})"


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="delivery_crew", null=True, limit_choices_to={'groups__name': "Delivery crew"})
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2,default=0)
    date = models.DateField(default=date.today) 

    def __str__(self):
        return str(self.id)

    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    #unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    #price = models.DecimalField(max_digits=6,decimal_places=2)

    class Meta():
        unique_together = ('order','menuitem')
    def __str__(self):
        return str(self.id)