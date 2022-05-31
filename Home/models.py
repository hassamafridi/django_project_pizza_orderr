from tkinter import CASCADE
from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class PizzaCategory(BaseModel):
    category = models.CharField(max_length=255)


class Pizza(BaseModel):
    category = models.ForeignKey(PizzaCategory, on_delete=models.CASCADE, related_name='pizzaa')
    pizza_name = models.CharField(max_length=255)
    price = models.IntegerField(default=100)
    image = models.ImageField(upload_to='pizza')
    

class Cart(BaseModel):
    user = models.ForeignKey(User,null=True , on_delete=models.SET_NULL)
    is_paid = models.BooleanField(default=False)
    instamoji_id =models.CharField(max_length=1000)

    def get_sum_total(self):
        items=CartItem.objects.filter(cart=self).prefetch_related('pizza')
        print(items)

        sum = 0
        for item in items:
            sum += item.pizza.price
        return sum
class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartItems')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
