from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from order.models import User, MenuItem, Order, Session, StaffCall
from .decorators import login_required, admin_required


def login_view(request):
    """ログイン画面"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('management:dashboard')
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません')
    
    return render(request, 'management/login.html')


def logout_view(request):
    """ログアウト"""
    logout(request)
    return redirect('management:login')


@login_required
def dashboard(request):
    """ダッシュボード（注文管理）"""
    orders = Order.objects.select_related('session', 'session__table', 'menu_item').exclude(status='SERVED').order_by('ordered_at')
    staff_calls = StaffCall.objects.filter(status='PENDING').select_related('table', 'session').order_by('called_at')
    
    # 経過時間を計算
    now = timezone.now()
    for order in orders:
        elapsed = now - order.ordered_at
        order.elapsed_minutes = int(elapsed.total_seconds() / 60)
    
    return render(request, 'management/dashboard.html', {
        'orders': orders,
        'staff_calls': staff_calls
    })


@login_required
@require_POST
def update_order_status(request):
    """注文ステータス更新"""
    order_id = request.POST.get('order_id')
    new_status = request.POST.get('status')
    
    order = get_object_or_404(Order, id=order_id)
    order.status = new_status
    order.save()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def resolve_staff_call(request):
    """店員呼び出し対応済み"""
    call_id = request.POST.get('call_id')
    
    staff_call = get_object_or_404(StaffCall, id=call_id)
    staff_call.status = 'RESOLVED'
    staff_call.resolved_at = timezone.now()
    staff_call.save()
    
    return JsonResponse({'success': True})


@login_required
def print_receipt(request, session_id):
    """レシート印刷"""
    session = get_object_or_404(Session, id=session_id)
    orders = session.orders.all()
    
    return render(request, 'management/receipt.html', {
        'session': session,
        'orders': orders,
        'total_amount': session.total_amount
    })


@admin_required
def menu_management(request):
    """メニュー管理画面"""
    menu_items = MenuItem.objects.all()
    return render(request, 'management/menu_management.html', {
        'menu_items': menu_items
    })


@admin_required
@require_POST
def create_menu_item(request):
    """メニュー商品作成"""
    name = request.POST.get('name')
    price = request.POST.get('price')
    image = request.FILES.get('image')
    
    if not name or not price or not image:
        return JsonResponse({'error': '必須項目が不足しています'}, status=400)
    
    menu_item = MenuItem.objects.create(
        name=name,
        price=int(price),
        image=image
    )
    
    return JsonResponse({'success': True, 'item_id': menu_item.id})


@admin_required
@require_POST
def update_menu_item(request, item_id):
    """メニュー商品更新"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    name = request.POST.get('name')
    price = request.POST.get('price')
    is_available = request.POST.get('is_available') == 'true'
    image = request.FILES.get('image')
    
    if name:
        menu_item.name = name
    if price:
        menu_item.price = int(price)
    
    menu_item.is_available = is_available
    
    if image:
        menu_item.image = image
    
    menu_item.save()
    
    return JsonResponse({'success': True})


@admin_required
@require_POST
def delete_menu_item(request, item_id):
    """メニュー商品削除"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    menu_item.delete()
    
    return JsonResponse({'success': True})


@admin_required
def sales_report(request):
    """売上管理画面"""
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    # 当月の完了セッション
    completed_sessions = Session.objects.filter(
        status='COMPLETED',
        completed_at__gte=month_start,
        completed_at__lte=month_end
    )
    
    # 日別売上
    daily_sales = {}
    for session in completed_sessions:
        day = session.completed_at.date()
        if day not in daily_sales:
            daily_sales[day] = 0
        daily_sales[day] += session.total_amount
    
    # 時間帯別売上（0-23時）
    hourly_sales = {i: 0 for i in range(24)}
    for session in completed_sessions:
        hour = session.completed_at.hour
        hourly_sales[hour] += session.total_amount
    
    # 商品別売上ランキング
    product_sales = Order.objects.filter(
        session__in=completed_sessions
    ).values('menu_item__name').annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum(F('quantity') * F('menu_item__price'))
    ).order_by('-total_sales')
    
    return render(request, 'management/sales.html', {
        'daily_sales': sorted(daily_sales.items()),
        'hourly_sales': sorted(hourly_sales.items()),
        'product_sales': product_sales,
        'month': month_start.strftime('%Y年%m月')
    })


@admin_required
def user_management(request):
    """ユーザー管理画面"""
    users = User.objects.all()
    return render(request, 'management/users.html', {
        'users': users
    })


@admin_required
@require_POST
def create_user(request):
    """ユーザー作成"""
    username = request.POST.get('username')
    password = request.POST.get('password')
    role = request.POST.get('role')
    
    if not username or not password or not role:
        return JsonResponse({'error': '必須項目が不足しています'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'このユーザー名は既に使用されています'}, status=400)
    
    user = User.objects.create_user(
        username=username,
        password=password,
        role=role
    )
    
    return JsonResponse({'success': True, 'user_id': user.id})


@admin_required
@require_POST
def update_user(request, user_id):
    """ユーザー更新"""
    user = get_object_or_404(User, id=user_id)
    
    password = request.POST.get('password')
    role = request.POST.get('role')
    is_active = request.POST.get('is_active') == 'true'
    
    if password:
        user.set_password(password)
    
    if role:
        user.role = role
    
    user.is_active = is_active
    user.save()
    
    return JsonResponse({'success': True})


@admin_required
@require_POST
def delete_user(request, user_id):
    """ユーザー削除"""
    if user_id == request.user.id:
        return JsonResponse({'error': '自分自身は削除できません'}, status=400)
    
    user = get_object_or_404(User, id=user_id)
    user.delete()
    
    return JsonResponse({'success': True})

