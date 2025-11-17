from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse

# Root view
def root(request):
    return JsonResponse({"message": "Backend is running!"})

# Favicon view
def favicon(request):
    # Return 204 No Content so browser stops requesting it
    return HttpResponse(status=204)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    path('', root),
    path('favicon.ico', favicon),
]
