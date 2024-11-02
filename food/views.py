from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, FoodItem,Order,Review,OrderItem,Payment
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import CategorySerializer, FoodItemSerializer,OrderSerializer,ReviewSerializer,OrderItemSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsAdminOrReadOnly
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.db.models import Count



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
    

class CategoryMenuCountAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        categories = Category.objects.annotate(menu_count=Count('food_items'))  
        response_data = [
            {
                'id': category.id,
                'name': category.name,
                'menu_count': category.menu_count
            }
            for category in categories
        ]
        
        return Response(response_data, status=status.HTTP_200_OK)



class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            # Save the order and associate it with the authenticated user
            order = serializer.save(user=request.user)

            # Serialize the order items to include in the response
            order_items = order.order_items.all()
            order_items_data = OrderItemSerializer(order_items, many=True).data

            return Response({
                'success': True,
                'order_id': order.id,
                'order_items': order_items_data  
            }, status=status.HTTP_201_CREATED)

       
        print("Serializer errors:", serializer.errors)
        return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




    def get(self, request, order_item_id=None, order_id=None, user_id=None):
        if order_item_id:
            
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
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response({'success': False, 'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            order.delete() 
            return Response({'success': True, 'message': 'Order deleted successfully'}, status=status.HTTP_200_OK)
        
        return Response({'success': False, 'message': 'Order ID not provided'}, status=status.HTTP_400_BAD_REQUEST)




# for payment gatway


from sslcommerz_lib import SSLCOMMERZ
from django.http import JsonResponse
import random
import string
import json
from django.views.decorators.csrf import csrf_exempt

def unique_transaction_id__generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@csrf_exempt
def payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        print(user_id)
        print(request.user)
        # Extract order and payment information from request
        total_price = data.get('total_price')
        full_name = data.get('full_name')
        email = data.get('email')
        address = data.get('address')
        city = data.get('city')
        cus_phone = "01500000000"

        # for production
        settings = {
            'store_id': 'quick672318e13dcd0',
            'store_pass': 'quick672318e13dcd0@ssl',
            'issandbox': True
        }

        # for local
        # settings = {
        #     'store_id': 'quick671dd3dff0df1',
        #     'store_pass': 'quick671dd3dff0df1@ssl',
        #     'issandbox': True
        # }

        sslcz = SSLCOMMERZ(settings)
        trans_id = unique_transaction_id__generator()

        # Define the post body for SSLCOMMERZ session
        post_body = {
            'total_amount': total_price,
            'currency': "BDT",
            'tran_id': trans_id,
            'success_url': "https://fooddelivery-lyart.vercel.app/food/success/",
            'fail_url': "https://fooddelivery-lyart.vercel.app/food/fail/",
            'cancel_url': "https://fooddelivery-lyart.vercel.app/food/cancel/",
            'emi_option': 0,
            'cus_name': full_name,
            'cus_email': email,
            'cus_phone': cus_phone,
            'cus_add1': address,
            'cus_city': city,
            'cus_country': "Bangladesh",
            'shipping_method': "NO",
            'num_of_item': len(data.get('order_items', [])),
            'product_name': "Food Items",
            'product_category': "Food",
            'product_profile': "general"
        }
        try:
            user = User.objects.get(id=user_id)  
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        print(user)
        print(trans_id)

        payment = Payment.objects.create(
            transaction_id=trans_id,
            user=user,
            user_id=user_id,
            status="initiated",  
            total_price=total_price,
            method="gateway",  
            full_name=full_name,
            email=email,
            address=address,
            city=city,
        )

       
        response = sslcz.createSession(post_body)
        if 'GatewayPageURL' in response:
            return JsonResponse({
                'GatewayPageURL': response['GatewayPageURL'],
                'transaction_id': trans_id
            })
        else:
            return JsonResponse({'error': 'Failed to create payment session'}, status=400)

       
    return JsonResponse({'error': 'Invalid request method'}, status=405)




@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Capture unique transaction ID sent back by SSLCOMMERZ
        transaction_id = data.get('transaction_id')
        print(transaction_id)

        try:
            # Update payment status for the transaction
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.status = "paid"
            payment.method = "gateway"
            payment.save()

            request.session['payment_confirmed'] = True

            return JsonResponse({'success': 'Order payment confirmed and updated.'})

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)




@csrf_exempt
def PaymentSuccessView(request):
    return render(request, "success.html")

@csrf_exempt
def PaymentFailView(request):
    return render(request, "fail.html")

@csrf_exempt
def PaymentCancelView(request):
    return render(request, "cancel.html")






class ReviewCreateAPIView(APIView):
    permission_classes = [IsAuthenticated] 

   
    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Extract food item and review details from the request data
        food_item_id = request.data.get('food_item')  # Get the food item ID
        rating = request.data.get('rating')
        review_text = request.data.get('review_text')

        # Ensure required fields are provided
        if not food_item_id or not rating or not review_text:
            return Response({'error': 'Food item, rating, and review text are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure rating is a valid integer (between 1 and 5)
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            return Response({'error': 'Rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the food item exists
        food_item = get_object_or_404(FoodItem, id=food_item_id)

        # Check if the user already left a review for this food item
        if Review.objects.filter(user=user, food_item=food_item).exists():
            return Response({'error': 'You have already reviewed this food item.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new review using the serializer
        review_data = {
            'food_item': food_item.id,  # Assign the food item ID 
            'rating': rating,
            'review_text': review_text
        }

        
        serializer = ReviewSerializer(data=review_data, context={'request': request})
        if serializer.is_valid():
            review = serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    def get(self, request, *args, **kwargs):
        user = request.user
        food_item_id = request.query_params.get('food_item_id')

        if food_item_id:
            reviews = Review.objects.filter(food_item_id=food_item_id)  # Retrieve reviews for the specific food item
        else:
            reviews = Review.objects.all()  # Get all reviews 

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ReviewListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        food_item_id = request.query_params.get('food_item_id')
        
        if not food_item_id:
            return Response({'error': 'Food item ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the food item exists
        food_item = get_object_or_404(FoodItem, id=food_item_id)

        # Retrieve reviews for the specified food item
        reviews = Review.objects.filter(food_item=food_item)

        # Serialize the reviews
        serializer = ReviewSerializer(reviews, many=True)

        # Return the serialized reviews
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    