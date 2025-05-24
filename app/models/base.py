from django.db.models import DateTimeField, Model
from rest_framework.generics import ListAPIView


class TimeModelBase(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class NonePaginationListAPIView(ListAPIView):
    pagination_class = None