# モバイルオーダーシステム

飲食店向けのモバイルオーダーシステムです。顧客はスマホから注文し、店舗スタッフは管理画面で注文管理・売上管理を行います。

## 機能概要

### 顧客向け機能
- QRコードからアクセス
- セッション管理（来店人数登録）
- 商品画像付きメニュー閲覧
- 注文機能（1商品あたり1-10個）
- 複数人同時注文対応
- 注文履歴確認
- 店員呼び出し機能
- 会計画面

### 店舗運用支援機能
- ログイン認証（管理者/スタッフ）
- 注文管理ダッシュボード
  - 未提供の注文一覧
  - 未会計・未提供の注文一覧
  - 未会計・全注文一覧
- 調理ステータス管理（未着手→調理中→完成→提供済）
- 店員呼び出し対応
- 会計・レシート印刷
  - 未会計セッション一覧表示
  - 会計完了処理
  - レシート印刷
- メニュー管理（管理者のみ）
  - 商品追加・編集・削除
  - 提供可能/不可切り替え
- 売上管理（管理者のみ）
  - 日別売上
  - 時間帯別売上
  - 商品別ランキング
- ユーザー管理（管理者のみ）

## 技術スタック

- Python 3.13
- Django 4.2.7
- SQLite3
- Bootstrap 5
- Pillow（画像処理）

## セットアップ

### クイックスタート（推奨）

```bash
# 1. 仮想環境作成・有効化
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 2. 依存関係インストール
pip install -r requirements.txt

# 3. データベース初期化
python manage.py migrate
python manage.py init_data

# 4. サーバー起動
python manage.py runserver
```

その後、ブラウザで以下にアクセス：
- 顧客画面: `http://127.0.0.1:8000/order?table=1`
- 管理画面: `http://127.0.0.1:8000/management/login/` (admin/admin123)

### 詳細手順

### 1. 仮想環境の作成と有効化

**Windowsの場合:**
```bash
# 仮想環境作成
python -m venv venv

# 仮想環境有効化
venv\Scripts\activate
```

**macOS/Linuxの場合:**
```bash
# 仮想環境作成
python -m venv venv

# 仮想環境有効化
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. データベースマイグレーション

```bash
python manage.py migrate
```

### 4. 初期データ投入

```bash
python manage.py init_data
```

以下のデータが作成されます：
- 管理者ユーザー: `admin` / `admin123`
- スタッフユーザー: `staff` / `staff123`
- テーブル: 1-10番（各4席）
- サンプル商品: 8商品

### 5. 開発サーバー起動

```bash
python manage.py runserver
```

## 使い方

### PC（開発環境）での動作確認

1. ブラウザで `http://127.0.0.1:8000/order?table=1` にアクセス
2. 来店人数を入力してセッション開始
3. メニューから商品を選択して注文
4. 注文履歴で状態を確認
5. 必要に応じて店員呼び出し
6. 会計画面で合計金額を確認

### スマホからのアクセス（ngrok経由）

1. **ngrokのインストール**
   
   - https://ngrok.com/ にアクセスしてアカウント作成（無料）
   - ngrokをダウンロード・インストール
   - 認証トークンを設定（初回のみ）：
     ```bash
     ngrok config add-authtoken YOUR_AUTH_TOKEN
     ```

2. **サーバー起動**
   ```bash
   python manage.py runserver
   ```

3. **ngrok起動（別ターミナル）**
   ```bash
   ngrok http 8000
   ```
   
   表示されるURL（例: `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app`）をメモ

4. **Djangoの設定を変更**
   
   `mobile_order/settings.py`を編集：
   ```python
   ALLOWED_HOSTS = ['xxxx-xx-xx-xxx-xxx.ngrok-free.app', 'localhost', '127.0.0.1']
   CSRF_TRUSTED_ORIGINS = ['https://xxxx-xx-xx-xxx-xxx.ngrok-free.app']
   ```
   （xxxx部分はngrokのURLに置き換える）

5. **サーバーを再起動**
   ```bash
   # Ctrl+Cで停止後、再起動
   python manage.py runserver
   ```

6. **スマホからアクセス**
   
   ブラウザで `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app/order?table=1` にアクセス

### 管理画面

1. `http://127.0.0.1:8000/management/login/` にアクセス
2. ユーザー名とパスワードでログイン
3. ダッシュボードで注文管理
4. メニュー管理、売上管理、ユーザー管理（管理者のみ）

#### ダッシュボードの注文一覧切り替え

ダッシュボードでは3つの表示モードを切り替えられます：

- **未提供**: 提供済以外の全注文（調理管理用）
  - ステータス変更が可能
  - 経過時間を表示
  
- **未会計・未提供**: 未会計かつ未提供の注文
  - 会計前の調理状況確認用
  - 金額情報を表示
  
- **未会計・全注文**: 未会計の全注文（提供済含む）
  - 会計時の最終確認用
  - 全注文の金額を表示

#### 会計・レシート印刷の使い方

1. ダッシュボード右側の「会計・レシート印刷」カードを確認
2. 未会計のセッション一覧から対象セッションをクリック
   - セッションID、テーブル番号、人数、合計金額が表示される
3. 「会計・レシート印刷」ボタンをクリック
4. 自動的に会計完了処理が実行され、レシート画面が開く
5. レシート画面で印刷または閉じる

## URL一覧

### 顧客向け
- `/order?table=<テーブル番号>` - セッション開始
- `/order/menu/` - メニュー一覧
- `/order/history/` - 注文履歴
- `/order/call-staff/` - 店員呼び出し
- `/order/payment/` - 会計

### 管理画面
- `/management/login/` - ログイン
- `/management/dashboard/` - ダッシュボード
- `/management/menu/` - メニュー管理（管理者のみ）
- `/management/sales/` - 売上管理（管理者のみ）
- `/management/users/` - ユーザー管理（管理者のみ）

## ディレクトリ構成

```
mobileOrderDjango/
├── venv/                        # 仮想環境（.gitignoreに追加推奨）
├── manage.py
├── requirements.txt
├── README.md
├── design.md                    # 設計書
├── youken.md                    # 要件定義書
├── db.sqlite3                   # データベース
├── mobile_order/                # プロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── order/                       # 注文アプリ
│   ├── models.py               # データモデル
│   ├── views.py                # ビュー
│   ├── urls.py                 # URLルーティング
│   ├── management/             # 管理コマンド
│   │   └── commands/
│   │       └── init_data.py   # 初期データ投入
│   └── templates/order/        # テンプレート
├── management_app/              # 管理アプリ
│   ├── views.py
│   ├── urls.py
│   ├── decorators.py           # 権限チェック
│   └── templates/management/
└── media/                       # アップロード画像
    └── menu/
        ├── original/
        ├── thumbnail/
        └── large/
```

## データモデル

### User
- ユーザー名、パスワード、権限（ADMIN/STAFF）

### Table
- テーブル番号（1-10）、座席数

### MenuItem
- 商品名、価格、画像、提供可能フラグ

### Session
- テーブル、来店人数、ステータス（ACTIVE/COMPLETED）

### Order
- セッション、商品、数量、ステータス（PENDING/COOKING/COMPLETED/SERVED）

### StaffCall
- セッション、テーブル、理由、ステータス（PENDING/RESOLVED）

## 注意事項

- このシステムはプロトタイプです
- 本番環境での使用は想定していません
- セキュリティ設定は最小限です
- 開発サーバーでのみ動作確認しています

## ライセンス

プロトタイプのため、ライセンスは設定していません。
