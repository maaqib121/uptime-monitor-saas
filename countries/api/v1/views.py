from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from countries.models import Country
from countries.api.v1.serializers import CountrySerializer


class CountryView(APIView):
    permission_classes = (AllowAny,)

    def get_queryset(self):
        country_qs = Country.objects.all()

        if self.request.GET.get('is_active'):
            is_active = True if self.request.GET['is_active'] == 'true' else False
            country_qs = country_qs.filter(is_active=is_active)

        if self.request.GET.get('search'):
            country_qs = country_qs.filter(name__icontains=self.request.GET['search'])

        return country_qs

    def get(self, request):
        serializer = CountrySerializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
