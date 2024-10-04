from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, FoodItem,Order,Review,OrderItem
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import CategorySerializer, FoodItemSerializer,OrderSerializer,ReviewSerializer,OrderItemSerializer
# from .permissions import IsAdmin
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsAdminOrReadOnly
from django.shortcuts import get_object_or_404

User = get_user_model()

class CategoryListView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        # Only admins can post
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class FoodItemsByCategoryAPIView(APIView):

    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, category_name=None, id=None):
        if id is not None:
            # Fetch the specific food item by ID
            try:
                food_item = FoodItem.objects.get(id=id)
                serializer = FoodItemSerializer(food_item)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except FoodItem.DoesNotExist:
                return Response({'detail': 'Food item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if category_name == 'all':
            food_items = FoodItem.objects.all()
        else:
            try:
                category = Category.objects.get(name=category_name)
                food_items = FoodItem.objects.filter(category=category)
            except Category.DoesNotExist:
                return Response({'detail': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FoodItemSerializer(food_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, category_name=None):
        # Only admins can post
        serializer = FoodItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, id=None):
        # Only admins can update (PUT) a specific food item
        try:
            food_item = FoodItem.objects.get(id=id)
        except FoodItem.DoesNotExist:
            return Response({'detail': 'Food item not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FoodItemSerializer(food_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id=None):
        # Only admins can delete a specific food item
        try:
            food_item = FoodItem.objects.get(id=id)
        except FoodItem.DoesNotExist:
            return Response({'detail': 'Food item not found'}, status=status.HTTP_404_NOT_FOUND)

        food_item.delete()
        return Response({'detail': 'Food item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    





class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Log incoming request data
       
        serializer = OrderSerializer(data=request.data)
       
        if serializer.is_valid():
            # Save the order and associate it with the authenticated user
            order = serializer.save(user=request.user)

            # Retrieve the order items from the validated data
            order_items_data = request.data.get('order_items', [])
            print("Order items data:", order_items_data)  # Log order items

            # Create the associated order items
            for item_data in order_items_data:
                # Retrieve the food_item from the database using the provided food_item ID
                food_item_id = item_data.get('food_item')
                try:
                    food_item = FoodItem.objects.get(id=food_item_id)
                except FoodItem.DoesNotExist:
                    print(f"Invalid FoodItem ID: {food_item_id}")
                    return Response({'success': False, 'message': 'Invalid FoodItem ID'}, status=status.HTTP_400_BAD_REQUEST)

                # Capture the name from the frontend, if available, else use food_item's name
                name = item_data.get('name', food_item.name)

                # Create the OrderItem with the provided name
                OrderItem.objects.create(
                    order=order,
                    food_item=food_item,
                    name=name,  # Use the name from the request or fallback to food_item.name
                    quantity=item_data.get('quantity', 1),
                    price=food_item.price  # Set the price from the food_item
                )

            # Serialize the order items to include in the response
            order_items = order.order_items.all()
            order_items_data = OrderItemSerializer(order_items, many=True).data

            return Response({
                'success': True,
                'order_id': order.id,
                'order_items': order_items_data  # Return serialized order items
            }, status=status.HTTP_201_CREATED)

        # If the serializer is invalid, log errors
        print("Serializer errors:", serializer.errors)
        return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, order_item_id=None, order_id=None, user_id=None):
        if order_item_id:
            # Filter orders by order item ID
            try:
                order_item = OrderItem.objects.get(id=order_item_id)
                order = order_item.order  # Get the order associated with this order item
            except OrderItem.DoesNotExist:
                return Response({'success': False, 'message': 'Order Item not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = OrderSerializer(order)
            return Response({'success': True, 'order': serializer.data}, status=status.HTTP_200_OK)

        elif user_id:
            # Retrieve all orders for the specified user ID
            try:
                user = User.objects.get(id=user_id)
                orders = Order.objects.filter(user=user)
            except User.DoesNotExist:
                return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        elif order_id:
            # Retrieve a specific order by ID for the authenticated user
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return Response({'success': False, 'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the specific order
            serializer = OrderSerializer(order)
            return Response({'success': True, 'order': serializer.data}, status=status.HTTP_200_OK)

        else:
            orders = Order.objects.all()

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def patch(self, request, order_id=None):
        # Partial update of the order
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return Response({'success': False, 'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            
            print("Incoming data:", request.data)

            # Use partial=True to allow partial updates
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'order': serializer.data}, status=status.HTTP_200_OK)
            return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': False, 'message': 'Order ID not provided'}, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, order_id=None):
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=request.user)  # Delete for the authenticated user
            except Order.DoesNotExist:
                return Response({'success': False, 'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            order.delete()  # Delete the order
            return Response({'success': True, 'message': 'Order deleted successfully'}, status=status.HTTP_200_OK)
        
        return Response({'success': False, 'message': 'Order ID not provided'}, status=status.HTTP_400_BAD_REQUEST)




# review

# class ReviewCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

#     # POST method for creating a review
#     def post(self, request, *args, **kwargs):
#         # Get the authenticated user
#         user = request.user
        
#         # Extract order and review details from the request data
#         order_id = request.data.get('order')
#         rating = request.data.get('rating')
#         review_text = request.data.get('review_text')

#         # Ensure the order exists and belongs to the user
#         order = get_object_or_404(Order, id=order_id, user=user)

#         # Check if the user already left a review for this order
#         if Review.objects.filter(user=user, order=order).exists():
#             return Response({'error': 'You have already reviewed this order.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Create a new review
#         review = Review.objects.create(
#             user=user,
#             order=order,
#             rating=rating,
#             review_text=review_text
#         )

#         # Serialize the newly created review and return a response
#         serializer = ReviewSerializer(review)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     # GET method for retrieving reviews
#     def get(self, request, *args, **kwargs):
#         # Get the authenticated user
#         user = request.user

#         # Optionally filter reviews by order if an 'order' query parameter is provided
#         order_id = request.query_params.get('order')

#         if order_id:
#             # Get reviews for a specific order that belongs to the user
#             order = get_object_or_404(Order, id=order_id, user=user)
#             reviews = Review.objects.filter(order=order)
#         else:
#             # Get all reviews made by the user
#             reviews = Review.objects.all()

#         # Serialize the reviews
#         serializer = ReviewSerializer(reviews, many=True)
        
#         # Return the serialized reviews
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class ReviewCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

#     # POST method for creating a review
#     def post(self, request, *args, **kwargs):
#         # Get the authenticated user
#         user = request.user
        
#         # Extract order and review details from the request data
#         order_id = request.data.get('order')
#         rating = request.data.get('rating')
#         review_text = request.data.get('review_text')

#         # Ensure the order exists and belongs to the user
#         order = get_object_or_404(Order, id=order_id, user=user)

#         # Check if the order status is 'delivered'
#         if order.order_status != 'delivered':
#             return Response({'error': 'You can only review an order once it has been delivered.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if the user already left a review for this order
#         if Review.objects.filter(user=user, order=order).exists():
#             return Response({'error': 'You have already reviewed this order.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Create a new review
#         review = Review.objects.create(
#             user=user,
#             order=order,
#             rating=rating,
#             review_text=review_text
#         )

#         # Serialize the newly created review and return a response
#         serializer = ReviewSerializer(review)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     # GET method for retrieving reviews
#     def get(self, request, *args, **kwargs):
#         # Get the authenticated user
#         user = request.user

#         # Optionally filter reviews by order if an 'order' query parameter is provided
#         order_id = request.query_params.get('order')

#         if order_id:
#             # Get reviews for a specific order that belongs to the user
#             order = get_object_or_404(Order, id=order_id, user=user)
#             reviews = Review.objects.filter(order=order)
#         else:
#             # Get all reviews made by the user
#             reviews = Review.objects.all()

#         # Serialize the reviews
#         serializer = ReviewSerializer(reviews, many=True)
        
#         # Return the serialized reviews
#         return Response(serializer.data, status=status.HTTP_200_OK)





class ReviewCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Extract order and review details from the request data
        order_id = request.data.get('order')
        rating = request.data.get('rating')
        review_text = request.data.get('review_text')

        # Ensure required fields are provided
        if not order_id or not rating or not review_text:
            return Response({'error': 'Order, rating, and review text are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure rating is a valid integer (between 1 and 5)
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            return Response({'error': 'Rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the order exists and belongs to the user
        order = get_object_or_404(Order, id=order_id, user=user)

        # Check if the order status is 'delivered'
        if order.order_status.lower() != 'delivered':  # Case insensitive check
            return Response({'error': 'You can only review an order once it has been delivered.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already left a review for this order
        if Review.objects.filter(user=user, order=order).exists():
            return Response({'error': 'You have already reviewed this order.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new review using the serializer
        review_data = {
            'user': user.id,  # Explicitly assign the user ID
            'rating': rating,
            'review_text': review_text
        }

        serializer = ReviewSerializer(data=review_data)
        if serializer.is_valid():
            review = serializer.save()  # Save the review
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user = request.user

        # Optionally filter reviews by order if an 'order' query parameter is provided
        order_id = request.query_params.get('order')

        if order_id:
            order = get_object_or_404(Order, id=order_id, user=user)
            reviews = Review.objects.filter(order=order)
        else:
            reviews = Review.objects.filter(user=user)  # Get all reviews for the user

        # Serialize the reviews
        serializer = ReviewSerializer(reviews, many=True)

        # Return the serialized reviews
        return Response(serializer.data, status=status.HTTP_200_OK)