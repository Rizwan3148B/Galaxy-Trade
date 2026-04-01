# Create your models here.
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model replacing Firebase Auth.
    Inherits username, email, password, and basic auth fields from Django.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    virtual_cash = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    email = models.EmailField(unique=True) # This strictly enforces 1 user per email
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.username

class Stock(models.Model):
    """
    The central directory for supported stocks.
    """
    symbol = models.CharField(max_length=10, primary_key=True)
    company_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True, null=True)

class Portfolio(models.Model):
    """
    This table tracks how many shares of a stock a specific user owns.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.PositiveIntegerField(default=0)

class Transaction(models.Model):
    """
    This table acts as the ledger, recording every buy and sell order.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    action = models.CharField(max_length=10) # Will store 'buy' or 'sell'
    shares = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.action} {self.shares} {self.stock.symbol} @ ${self.price}"

    def __str__(self):
        return f"{self.user.username} owns {self.shares} shares of {self.stock.symbol}"

    def __str__(self):
        return f"{self.symbol} - {self.company_name}"