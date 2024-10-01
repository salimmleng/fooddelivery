from django.urls import path
from .views import CategoryListView, FoodItemsByCategoryAPIView,CheckoutView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('food-items/<str:category_name>/', FoodItemsByCategoryAPIView.as_view(), name='food-items-by-category'),
    path('food-item/<int:id>/', FoodItemsByCategoryAPIView.as_view(), name='food-item-detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),



    path('checkout/user/<int:user_id>/', CheckoutView.as_view(), name='checkout_user'),
    
    path('checkout/order/<int:order_id>/', CheckoutView.as_view(), name='checkout_order'),

   
   

]