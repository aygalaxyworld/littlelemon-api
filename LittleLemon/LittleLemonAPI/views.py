from .serializer import (
    CategorySerializer,
    MenuItemSerializer,
    UserSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
)
from rest_framework.response import Response
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import date
from django.http import Http404
from .permissions import IsManagerOrReadOnly, IsManager, IsCustomer
from django.db.utils import IntegrityError
from .paginations import PageItemPagination
from .filters import OrderFilter, MenuItemFilter
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.


class Category_Items_view(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset

    serializer_class = CategorySerializer


class Menu_Items_view(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly | IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = MenuItemSerializer
    pagination_class = PageItemPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MenuItemFilter

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        return queryset

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Extract the category ID from request data
            category_title = serializer.validated_data.get("category")

            # Check if the specified category title exists
            try:
                category = Category.objects.get(title=category_title)
            except Category.DoesNotExist:
                return Response(
                    {"category": "Category with this ID does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create the MenuItem with the specified category
            serializer.save(category=category)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Single_Menu_Item_View(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    queryset = MenuItem.objects.all()


class Manager_View(generics.ListCreateAPIView):
    permission_classes = [IsManager | IsAdminUser]
    serializer_class = UserSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        queryset = User.objects.filter(groups__name="Managers")
        return queryset

    def create(self, request):
        group = Group.objects.get(name="Managers")
        username_to_assign = request.data.get("username")

        if username_to_assign:
            user = get_object_or_404(User, username=username_to_assign)
            if user.groups.filter(name="Managers").exists():
                return Response(
                    {"message": "User already assigned to group Manager."},
                    status=status.HTTP_200_OK,
                )
            group.user_set.add(user)
            return Response(
                {"message": "User assigned to group Manager successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"username": "This field is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class Remove_User_From_Manager_Group_View(generics.DestroyAPIView):
    permission_classes = [IsManager]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        # Use get_object_or_404 to retrieve the user or return a 404 response if not found
        user = get_object_or_404(User, pk=user_id)
        group = Group.objects.get(name="Managers")
        # Check if the user is in the group before removing
        if group in user.groups.all():
            group.user_set.remove(user)
            return Response(
                {"message": "User removed from group Manager successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "User is not in group Managers."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Delivery_Crew_View(generics.ListCreateAPIView):
    permission_classes = [IsManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.filter(groups__name="Delivery Crew")
        return queryset

    def create(self, request):
        group = Group.objects.get(name="Delivery Crew")
        username_to_assign = request.data.get("username")

        if username_to_assign:
            user = get_object_or_404(User, username=username_to_assign)
            if user.groups.filter(name="Delivery Crew").exists():
                return Response(
                    {"message": "User already assigned to group Delivery Crew."},
                    status=status.HTTP_200_OK,
                )
            group.user_set.add(user)
            return Response(
                {"message": "User assigned to group Delivery Crew successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"Username": "This field is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class Remove_User_From_Delivery_Crew_Group_View(generics.DestroyAPIView):
    permission_classes = [IsManager]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        # Use get_object_or_404 to retrieve the user or return a 404 response if not found
        user = get_object_or_404(User, pk=user_id)
        group = Group.objects.get(name="Delivery Crew")
        # Check if the user is in the group before removing
        if group in user.groups.all():
            group.user_set.remove(user)
            return Response(
                {"message": "User removed from group Delivery Crew successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "User is not in group Delivery Crew."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Cart_View(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CartSerializer

    def get_queryset(self):
        # Return current user's cart items or raise a 404 exception with a custom message
        queryset = Cart.objects.filter(user=self.request.user)
        if not queryset.exists():
            raise Http404("No items in cart")
        return queryset

    def perform_create(self, serializer):
        # Calculate unit_price and price for POST requests
        menuitem = serializer.validated_data["menuitem"]
        serializer.save(
            user=self.request.user,
            unit_price=menuitem.price,
            price=menuitem.price * serializer.validated_data["quantity"],
        )

    def create(self, request, *args, **kwargs):
        # Override create to use perform_create and return a 201-Created response
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError as e:
            return Response({"message": "Menu Item already in cart"})

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def delete(self, request, *args, **kwargs):
        # Delete all cart items associated with the current user and 'food' items
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Order_View(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = PageItemPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    ordering_fields = ["title", "price"]
    searching_fields = ["title"]

    def get_queryset(self):
        user = self.request.user
        # Check if the user belongs to the 'manager' group
        manager_group = get_object_or_404(Group, name="Managers")
        if manager_group in user.groups.all():
            # Users in the 'manager' group can retrieve all orders
            return OrderItem.objects.all()
        # Check if the user belongs to the 'delivery crew' group
        delivery_crew_group = get_object_or_404(Group, name="Delivery Crew")
        if delivery_crew_group in user.groups.all():
            # Users in the 'delivery crew' group can retrieve orders assigned to them
            return OrderItem.objects.filter(order__delivery_crew=user)

        # Default behavior for users without a specific group
        # # They can retrieve their own orders
        return OrderItem.objects.filter(order__user=user)

    def create(self, request, *args, **kwargs):
        user = self.request.user

        cart_user = Cart.objects.filter(user=user)
        if not cart_user:
            return Response(
                {"message": "No Cart by this user"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Calculate the total price of cart items
        cart_total = cart_user.aggregate(total_price=Sum("price"))["total_price"]

        # Create a new order for the user with status = False (Out for Delivery)
        order = Order.objects.create(
            user=user, status=bool(0), total=cart_total, date=date.today()
        )

        # Copy cart items to order items
        for cart_item in Cart.objects.filter(user=user):
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price,
            )

        # Delete all cart items associated with the user
        Cart.objects.filter(user=user).delete()

        serializer = self.get_serializer(order)
        headers = self.get_success_headers(serializer.data)
        serializer.data
        return Response(
            {"message": "The Order was taken successfully "},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class Single_Orders_view(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ["dates", "price"]

    def get_queryset(self):
        user = self.request.user
        queryset = OrderItem.objects.filter(order__user=user)
        return queryset

    def update(self, request, *args, **kwargs):
        user = request.user
        manager_group_exists = user.groups.filter(name="Managers").exists()
        delivery_crew_group_exists = user.groups.filter(name="Delivery Crew").exists()

        if manager_group_exists or delivery_crew_group_exists:
            order_id = kwargs.get("pk")
            order = get_object_or_404(Order, pk=order_id)

            # Update the order with the provided data
            delivery_crew_username = request.data.get("delivery_crew")
            delivery_status_state = int(request.data.get("delivery_status"))

            # Check if status is provided and valid
            if delivery_status_state in [0, 1]:
                order.status = delivery_status_state
            else:
                return Response(
                    {"message": "Enter 0 for out for delivery 1 for delivered."}
                )

            if not delivery_crew_group_exists and manager_group_exists:
                # Check if delivery_crew_id is provided and valid
                if delivery_crew_username:
                    delivery_crew = get_object_or_404(
                        User, username=delivery_crew_username
                    )
                    order.delivery_crew = delivery_crew

            order.save()

            # Optionally, you can return the updated order data
            serializer = self.get_serializer(order)

            return Response(serializer.data, status=status.HTTP_200_OK)

        if delivery_crew_group_exists:
            delivery_status_state = request.data.get("delivery_status")
            if delivery_status_state != 0 or delivery_status_state != 1:
                return Response({"message": "Input either 1 or 0"})

        return Response(
            {"message": "You don't have permission to update this order."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        order_id = kwargs.get("pk")

        # Check if the user belongs to the 'Managers' group
        manager_group_exists = user.groups.filter(name="Managers").exists()

        if manager_group_exists:
            try:
                order = Order.objects.get(id=order_id)
                order.delete()
                return Response(
                    {"message": "Order deleted successfully."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            except Order.DoesNotExist:
                raise Http404("Order does not exist.")
        else:
            return Response(
                {"message": "You don't have permission to delete this order."},
                status=status.HTTP_403_FORBIDDEN,
            )
