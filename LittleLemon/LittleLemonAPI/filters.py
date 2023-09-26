import django_filters
from .models import MenuItem, Order, OrderItem


class MenuItemFilter(django_filters.FilterSet):
    class Meta:
        model = MenuItem
        fields = ["title", "category", "price", "featured"]


class OrderFilter(django_filters.FilterSet):
    order__status = django_filters.CharFilter(method="filter_order_status")
    order__date = django_filters.DateFilter()

    class Meta:
        model = OrderItem
        fields = ["order__status", "order__date"]

    def filter_order_status(self, queryset, name, value):
        if value == "1":
            return queryset.filter(order__status=True)
        elif value == "0":
            return queryset.filter(order__status=False)
        return queryset.none()
