from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def rector_required(function=None):
    """
    Decorator for views that checks that the user is a rector.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_rector(),
        login_url='/accounts/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def dean_required(function=None):
    """
    Decorator for views that checks that the user is a dean.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_dean(),
        login_url='/accounts/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def tutor_required(function=None):
    """
    Decorator for views that checks that the user is a tutor.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_tutor(),
        login_url='/accounts/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
