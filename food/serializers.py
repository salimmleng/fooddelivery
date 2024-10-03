from rest_framework import serializers
from .models import Category, FoodItem, Order, OrderItem,Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class FoodItemSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name' 
    )
   
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'description', 'price','image','category']



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True,required=False)  # Match the related_name in the model

    full_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    card_number = serializers.CharField(required=False)
    expiry_date = serializers.CharField(required=False)
    cvv = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'full_name', 'email', 'address', 'city', 'card_number', 'expiry_date', 'cvv', 'total_price', 'order_items', 'created_at','order_status']
        read_only_fields = ["user"]

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')  # Match the field name in the serializer
        order = Order.objects.create(**validated_data)
        
        # Create the OrderItem objects and associate them with the order
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order
    


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Read-only username field
    order_items = OrderItemSerializer(many=True, source='order.order_items', read_only=True)  # Access related order items

    class Meta:
        model = Review
        fields = ['id', 'username', 'order_items', 'rating', 'review_text', 'created_at']