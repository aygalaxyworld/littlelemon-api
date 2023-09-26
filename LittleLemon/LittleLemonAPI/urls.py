from django.urls import path
from . import views

urlpatterns = [
    path('category',views.Category_Items_view.as_view()),
    path('menu-items', views.Menu_Items_view.as_view()),
    path('menu-items/<int:pk>', views.Single_Menu_Item_View.as_view()),
    path('groups/manager/users', views.Manager_View.as_view()),
    path('groups/manager/users/<int:pk>', views.Remove_User_From_Manager_Group_View.as_view()),
    path('groups/delivery-crew/users', views.Delivery_Crew_View.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.Remove_User_From_Delivery_Crew_Group_View.as_view()),
    path('cart/menu-items', views.Cart_View.as_view()),
    path('orders', views.Order_View.as_view()),
    path('orders/<int:pk>', views.Single_Orders_view.as_view()),
  
    
]