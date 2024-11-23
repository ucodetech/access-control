from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class RestrictAdminDashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Restrict access to superuser dashboard
        if request.path.startswith("/superuser/") and not (
            request.user.is_authenticated and (request.user.is_superuser or request.user.is_admin)
        ):
            messages.error(request, "You do not have permission to access this page.")
            return redirect(reverse('index'))  # replace 'login' with your actual login URL name
            # If user is authorized, proceed with the request
        response = self.get_response(request)
        return response




