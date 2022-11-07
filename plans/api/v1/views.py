from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from plans.models import Plan
from plans.api.v1.serializers import PlanSerializer


class PlanView(APIView):
    http_method_names = ('get',)
    permission_classes = (AllowAny,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Plan.objects.filter(Q(company__isnull=True) | Q(company=self.request.user.company))
        else:
            return Plan.objects.filter(company__isnull=True)

    def get(self, request):
        serializer = PlanSerializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
