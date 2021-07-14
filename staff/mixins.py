from django.shortcuts import redirect
from userbase.models import User


class StaffUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect("home")
        elif request.user.is_superuser:
            return redirect("home")
        return super(StaffUserMixin, self).dispatch(request, *args, **kwargs)
