from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from .models import Table, Session, MenuItem, Order, StaffCall
from django.utils import timezone


def start_session(request):
    """セッション開始画面"""
    table_id = request.GET.get('table')
    
    if not table_id:
        return render(request, 'order/error.html', {'message': 'テーブル番号が指定されていません'})
    
    table = get_object_or_404(Table, table_number=table_id)
    
    # アクティブなセッションをチェック
    active_session = Session.objects.filter(table=table, status='ACTIVE').first()
    
    if active_session:
        request.session['session_id'] = active_session.id
        return redirect('order:menu_list')
    
    return render(request, 'order/start_session.html', {'table': table})


@require_POST
def create_session(request):
    """セッション作成"""
    table_id = request.POST.get('table_id')
    guest_count = request.POST.get('guest_count')
    
    if not table_id or not guest_count:
        return JsonResponse({'error': '必須項目が不足しています'}, status=400)
    
    table = get_object_or_404(Table, table_number=table_id)
    
    # 新しいセッションを作成
    session = Session.objects.create(
        table=table,
        guest_count=int(guest_count)
    )
    
    request.session['session_id'] = session.id
    
    return JsonResponse({'success': True, 'redirect_url': '/order/menu/'})


def menu_list(request):
    """メニュー一覧画面"""
    session_id = request.session.get('session_id')
    
    if not session_id:
        return redirect('order:start_session')
    
    session = get_object_or_404(Session, id=session_id, status='ACTIVE')
    menu_items = MenuItem.objects.all()
    
    return render(request, 'order/menu.html', {
        'session': session,
        'menu_items': menu_items
    })


@require_POST
def submit_order(request):
    """注文送信"""
    session_id = request.session.get('session_id')
    menu_item_id = request.POST.get('menu_item_id')
    quantity = request.POST.get('quantity')
    
    if not session_id or not menu_item_id or not quantity:
        return JsonResponse({'error': '必須項目が不足しています'}, status=400)
    
    session = get_object_or_404(Session, id=session_id, status='ACTIVE')
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    
    # 注文を作成
    order = Order.objects.create(
        session=session,
        menu_item=menu_item,
        quantity=int(quantity)
    )
    
    return JsonResponse({
        'success': True,
        'message': f'{menu_item.name} x {quantity}を注文しました'
    })


def order_history(request):
    """注文履歴画面"""
    session_id = request.session.get('session_id')
    
    if not session_id:
        return redirect('order:start_session')
    
    session = get_object_or_404(Session, id=session_id)
    orders = session.orders.all()
    
    return render(request, 'order/history.html', {
        'session': session,
        'orders': orders
    })


def call_staff(request):
    """店員呼び出し画面"""
    session_id = request.session.get('session_id')
    
    if not session_id:
        return redirect('order:start_session')
    
    session = get_object_or_404(Session, id=session_id)
    
    return render(request, 'order/call_staff.html', {'session': session})


@require_POST
def submit_staff_call(request):
    """店員呼び出し送信"""
    session_id = request.session.get('session_id')
    reason = request.POST.get('reason')
    
    if not session_id or not reason:
        return JsonResponse({'error': '必須項目が不足しています'}, status=400)
    
    session = get_object_or_404(Session, id=session_id, status='ACTIVE')
    
    # 店員呼び出しを作成
    staff_call = StaffCall.objects.create(
        session=session,
        table=session.table,
        reason=reason
    )
    
    return JsonResponse({
        'success': True,
        'message': '店員を呼び出しました'
    })


def payment(request):
    """会計画面"""
    session_id = request.session.get('session_id')
    
    if not session_id:
        return redirect('order:start_session')
    
    session = get_object_or_404(Session, id=session_id)
    orders = session.orders.all()
    
    return render(request, 'order/payment.html', {
        'session': session,
        'orders': orders,
        'total_amount': session.total_amount
    })

