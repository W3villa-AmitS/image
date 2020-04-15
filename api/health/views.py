from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class HealthView(APIView):
    """
    Return okay if application is up and running
    """
    def get(self, request):
        # TODO add checks for database and result processing service.
        return Response({'Status': 'Active'}, status=status.HTTP_200_OK)