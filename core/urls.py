from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.authentication.urls", namespace="authentication")),
    path("home/", include("apps.home.urls", namespace="home")),
    path("sistema/", include("apps.sistema.urls", namespace="sistema")),
    path("financeiro/", include("apps.financeiro.urls", namespace="financeiro")),
    path("bancario/", include("apps.bancario.urls", namespace="bancario")),
    path("orcamento/", include("apps.orcamento.urls", namespace="orcamento")),
    path("fiscal/", include("apps.fiscal.urls", namespace="fiscal")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)