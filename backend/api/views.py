from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_message(request):
    return Response({"message": "Привіт з Django API!"})