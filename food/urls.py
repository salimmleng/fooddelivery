from django.urls import path
from .views import CategoryListView, FoodItemsByCategoryAPIView,CheckoutView,ReviewCreateAPIView,ReviewListAPIView,payment,PaymentCancelView,PaymentFailView,PaymentSuccessView,payment_success,CategoryMenuCountAPIView,ReviewAllAPIView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('food-items/<str:category_name>/', FoodItemsByCategoryAPIView.as_view(), name='food-items-by-category'),
    path('food-item/<int:id>/', FoodItemsByCategoryAPIView.as_view(), name='food-item-detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # count menu items

    path('categories/count/', CategoryMenuCountAPIView.as_view(), name='category-menu-count'),


    path('checkout/order-item/<int:order_item_id>/', CheckoutView.as_view(), name='order-by-item'),

    path('checkout/user/<int:user_id>/', CheckoutView.as_view(), name='checkout_user'),
    
    path('checkout/order/<int:order_id>/', CheckoutView.as_view(), name='checkout_order'),
    
    # review
    path('reviews/create/', ReviewCreateAPIView.as_view(), name='create-review'),
  
    path('reviews/', ReviewListAPIView.as_view(), name='get-reviews'),
     path('reviews_all/', ReviewAllAPIView.as_view(), name='get-reviews'),

    # payment

    path('payment/', payment, name='initiate_payment'),

    path('success/', PaymentSuccessView, name='payment_success'),
    path('fail/', PaymentFailView, name='payment_fail'),
    path('cancel/', PaymentCancelView, name='payment_cancel'),
    path('payment/success/', payment_success, name='payment_success'),

]