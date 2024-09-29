from rest_framework import serializers
from .models import Category, FoodItem, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class FoodItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'description', 'price']






class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)  # Match the related_name in the model
    class Meta:
        model = Order
        fields = ['id', 'user', 'full_name', 'email', 'address', 'city', 'card_number', 'expiry_date', 'cvv', 'total_price', 'order_items', 'created_at']
        read_only_fields = ["user"]

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')  # Match the field name in the serializer
        order = Order.objects.create(**validated_data)
        
        # Create the OrderItem objects and associate them with the order
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order