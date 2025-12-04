"""
モバイルオーダーシステム テストスクリプト
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_customer_flow():
    """顧客側の基本フローをテスト"""
    print("=== 顧客側フローテスト ===")
    
    # 1. セッション開始画面アクセス
    print("1. セッション開始画面アクセス...")
    response = requests.get(f"{BASE_URL}/order/?table=1")
    assert response.status_code == 200, "セッション開始画面の表示に失敗"
    print("   ✓ セッション開始画面表示成功")
    
    # 2. セッション作成
    print("2. セッション作成...")
    session = requests.Session()
    csrf_token = extract_csrf_token(response.text)
    response = session.post(
        f"{BASE_URL}/order/session/create/",
        data={"table_id": 1, "guest_count": 2, "csrfmiddlewaretoken": csrf_token}
    )
    assert response.status_code == 200, "セッション作成に失敗"
    data = response.json()
    assert data.get('success'), "セッション作成レスポンスが不正"
    print("   ✓ セッション作成成功")
    
    # 3. メニュー表示
    print("3. メニュー表示...")
    response = session.get(f"{BASE_URL}/order/menu/")
    assert response.status_code == 200, "メニュー表示に失敗"
    print("   ✓ メニュー表示成功")
    
    print("\n✅ 顧客側フローテスト完了\n")


def test_management_login():
    """管理画面ログインテスト"""
    print("=== 管理画面ログインテスト ===")
    
    # 1. ログイン画面アクセス
    print("1. ログイン画面アクセス...")
    session = requests.Session()
    response = session.get(f"{BASE_URL}/management/login/")
    assert response.status_code == 200, "ログイン画面の表示に失敗"
    print("   ✓ ログイン画面表示成功")
    
    # 2. ログイン実行
    print("2. ログイン実行...")
    csrf_token = extract_csrf_token(response.text)
    response = session.post(
        f"{BASE_URL}/management/login/",
        data={"username": "admin", "password": "admin123", "csrfmiddlewaretoken": csrf_token}
    )
    assert response.status_code == 200 or response.status_code == 302, "ログインに失敗"
    print("   ✓ ログイン成功")
    
    # 3. ダッシュボードアクセス
    print("3. ダッシュボードアクセス...")
    response = session.get(f"{BASE_URL}/management/dashboard/")
    assert response.status_code == 200, "ダッシュボード表示に失敗"
    print("   ✓ ダッシュボード表示成功")
    
    print("\n✅ 管理画面ログインテスト完了\n")


def extract_csrf_token(html):
    """HTMLからCSRFトークンを抽出（簡易版）"""
    import re
    # input要素のvalue属性から抽出
    match = re.search(r'name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']', html)
    if not match:
        # value="..."のパターンも試す
        match = re.search(r'value=["\']([^"\']+)["\'][^>]*name=["\']csrfmiddlewaretoken["\']', html)
    if match:
        return match.group(1)
    return ""


if __name__ == "__main__":
    try:
        print("モバイルオーダーシステム テスト開始\n")
        test_customer_flow()
        test_management_login()
        print("=" * 50)
        print("✅ すべてのテストが成功しました！")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n❌ テスト失敗: {e}")
    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
