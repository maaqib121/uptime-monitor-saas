from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from plans.models import Plan
from plans.api.v1.serializers import PlanSerializer
from users.permissions import IsCurrentUserAdmin


class PlanView(APIView):
    http_method_names = ('get',)

    def get_permissions(self):
        if self.request.user.is_authenticated:
            permission_classes = (IsAuthenticated, IsCurrentUserAdmin)
        else:
            permission_classes = (AllowAny,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Plan.objects.filter(Q(company__isnull=True) | Q(company=self.request.user.company))
        else:
            return Plan.objects.filter(company__isnull=True)

    def get(self, request):
        serializer = PlanSerializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
