from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views.auth import DashboardTokenObtainPairView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/', include([
        path('', include('core.router')),
        path('', include('negocios.router')),
        path('', include('clientes.router')),
        path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/dashboard', DashboardTokenObtainPairView.as_view(), name='token_dashboard'),
        path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    ]))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
