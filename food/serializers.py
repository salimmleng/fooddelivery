from rest_framework import serializers
from .models import Category, FoodItem, Order, OrderItem,Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class FoodItemSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name' 
    )
   
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'description', 'price','image','category']



class OrderItemSerializer(serializers.ModelSerializer):

    food_item = serializers.PrimaryKeyRelatedField(queryset=FoodItem.objects.all()) 
    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, required=False)  # Match the related_name in the model

    full_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    card_number = serializers.CharField(required=False)
    expiry_date = serializers.CharField(required=False)
    cvv = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'full_name', 'email', 'address', 'city', 'card_number', 'expiry_date', 'cvv', 'total_price', 'order_items', 'created_at', 'order_status']
        read_only_fields = ["user"]

    def create(self, validated_data):
    # Extract order_items data
        order_items_data = validated_data.pop('order_items', [])

    # Create the order
        order = Order.objects.create(**validated_data)

    # Create or update each order item
        for item_data in order_items_data:
            food_item = item_data.pop('food_item')  # Extract food_item ID
            quantity = item_data.get('quantity', 1)  # Default quantity to 1 if not provided

            # Check if the order item already exists
            existing_item = OrderItem.objects.filter(order=order, food_item=food_item).first()
        
            if existing_item:
                # Update quantity if the item already exists
                existing_item.quantity += quantity
                existing_item.save()
            else:
                # Create a new order item if it doesn't exist
                OrderItem.objects.create(order=order, food_item=food_item, quantity=quantity, **item_data)

        return order


    





class ReviewSerializer(serializers.ModelSerializer):
    # The 'food_item' field is now a required field
    food_item = serializers.PrimaryKeyRelatedField(queryset=FoodItem.objects.all())
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'food_item', 'rating', 'review_text', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user 
        return super().create(validated_data)

   