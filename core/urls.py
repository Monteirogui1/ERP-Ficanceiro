from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("authentication.urls", namespace="authentication")),
    path("cadastros/", include("cadastros.urls", namespace="cadastros")),
    path("financeiro/", include("financeiro.urls", namespace="financeiro")),
    path("bancario/", include("bancario.urls", namespace="bancario")),
    path("orcamento/", include("orcamento.urls", namespace="orcamento")),
    path("fiscal/", include("fiscal.urls", namespace="fiscal")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)