from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers.auth import DashboardTokenObtainPairSerializer

class DashboardTokenObtainPairView(TokenObtainPairView):
    serializer_class = DashboardTokenObtainPairSerializer
    permission_classes = (AllowAny,)
