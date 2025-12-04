from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def login_required(view_func):
    """ログイン必須デコレータ"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'ログインが必要です')
            return redirect('management:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """管理者権限必須デコレータ"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'ログインが必要です')
            return redirect('management:login')
        if request.user.role != 'ADMIN':
            messages.error(request, '管理者権限が必要です')
            return redirect('management:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
