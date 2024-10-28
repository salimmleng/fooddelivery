from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.URLField(max_length=200)

    def __str__(self):
        return self.name
    

ORDER_STATUS = [
    ('Delivered','Delivered'),
    ('Pending','Pending'),
]


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(choices=ORDER_STATUS,max_length=20,default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"{self.quantity} x {self.name}"
    



class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Associate with the user
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE,null=True) # Reference to the order
    rating = models.IntegerField()
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        food_item_name = self.food_item.name if self.food_item else "No Food Item"
        return f"Review by {self.user.username} for Food Item: {food_item_name}"
