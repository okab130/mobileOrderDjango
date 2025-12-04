# モバイルオーダーシステム 設計書

## 1. データモデル設計

### 1.1 エンティティ一覧

#### User（ユーザー）
- Djangoの標準User拡張
- フィールド:
  - username (ログインID)
  - password (パスワード)
  - role (権限: ADMIN/STAFF)
  - is_active (有効/無効)

#### Table（テーブル）
- フィールド:
  - table_number (テーブル番号: 1-10)
  - seat_count (座席数)
  - qr_code_url (QRコードURL)

#### MenuItem（メニュー商品）
- フィールド:
  - name (商品名)
  - price (価格)
  - image (商品画像)
  - thumbnail (サムネイル画像)
  - is_available (提供可能フラグ)
  - created_at (登録日時)
  - updated_at (更新日時)

#### Session（注文セッション）
- フィールド:
  - table (テーブル)
  - guest_count (来店人数)
  - status (ステータス: ACTIVE/COMPLETED)
  - started_at (開始日時)
  - completed_at (終了日時)

#### Order（注文）
- フィールド:
  - session (セッション)
  - menu_item (商品)
  - quantity (数量: 1-10)
  - status (ステータス: PENDING/COOKING/COMPLETED/SERVED)
  - ordered_at (注文日時)
  - updated_at (更新日時)

#### StaffCall（店員呼び出し）
- フィールド:
  - session (セッション)
  - table (テーブル)
  - reason (理由: WATER/PAYMENT/QUESTION/COMPLAINT/OTHER)
  - status (ステータス: PENDING/RESOLVED)
  - called_at (呼び出し日時)
  - resolved_at (対応完了日時)

### 1.2 ER図（テキスト表記）

```
User (1) --- manages ---> (N) MenuItem
User (1) --- manages ---> (N) Order
User (1) --- manages ---> (N) StaffCall

Table (1) --- has ---> (N) Session
Table (1) --- has ---> (N) StaffCall

Session (1) --- has ---> (N) Order
Session (1) --- has ---> (N) StaffCall

MenuItem (1) --- referenced by ---> (N) Order
```

### 1.3 制約・ルール

- テーブルは1-10の固定（初期データ）
- 注文数量は1-10の範囲
- セッションは同一テーブルで複数アクティブ不可（会計完了後に新規作成）
- 注文ステータス遷移: PENDING → COOKING → COMPLETED → SERVED
- 店員呼び出しは未対応のもののみ表示（対応済みは論理削除せず履歴非表示）

---

## 2. 機能設計

### 2.1 顧客向け機能（スマホ）

#### 2.1.1 セッション開始画面
- URL: `/order?table=<table_id>`
- 機能: 来店人数入力、セッション作成
- 画面遷移: → メニュー一覧画面

#### 2.1.2 メニュー一覧・注文画面
- 機能: 
  - 商品一覧表示（サムネイル、商品名、価格）
  - 商品詳細モーダル（大サイズ画像）
  - 数量選択（1-10）
  - 注文確定ボタン（即座にサーバー送信）
  - 売り切れ商品のグレーアウト表示

#### 2.1.3 注文履歴画面
- 機能: 現在セッションの注文一覧（商品名、数量、注文時刻、ステータス）
- リロードボタンで最新情報取得

#### 2.1.4 店員呼び出し画面
- 機能: 理由選択（お水、会計、質問、苦情、その他）、呼び出しボタン

#### 2.1.5 会計画面
- 機能: 合計金額表示、注文明細表示
- 常時表示（セッション開始後）

### 2.2 店舗運用支援機能（管理画面）

#### 2.2.1 ログイン画面
- 機能: ユーザー名・パスワード入力、認証

#### 2.2.2 ダッシュボード（注文管理）
- 機能:
  - 全注文一覧表示（注文日時古い順）
  - 表示項目: テーブル番号、商品名、数量、注文日時、経過時間、ステータス
  - ステータス変更ボタン（PENDING→COOKING→COMPLETED→SERVED）
  - 店員呼び出し一覧（未対応のみ）
  - 呼び出し対応済みボタン
  - レシート印刷ボタン（テーブル単位）

#### 2.2.3 メニュー管理画面（管理者のみ）
- 機能:
  - 商品一覧表示
  - 商品追加・編集・削除
  - 画像アップロード（ドラッグ&ドロップ）
  - 自動リサイズ（サムネイル300x300、大サイズ1200x900）
  - 提供可能フラグ変更

#### 2.2.4 売上管理画面（管理者のみ）
- 機能:
  - 当月の日別売上集計
  - 当月の時間帯別売上（1時間単位）
  - 商品別売上ランキング（全商品、金額順）

#### 2.2.5 ユーザー管理画面（管理者のみ）
- 機能:
  - ユーザー一覧表示
  - ユーザー追加・編集・削除
  - 権限設定（ADMIN/STAFF）

---

## 3. 画面一覧

### 3.1 顧客向け画面（スマホ）
1. セッション開始画面（`/order?table=<id>`）
2. メニュー一覧画面（`/order/menu`）
3. 注文履歴画面（`/order/history`）
4. 店員呼び出し画面（`/order/call-staff`）
5. 会計画面（`/order/payment`）

### 3.2 店舗管理画面（PC）
1. ログイン画面（`/admin/login`）
2. ダッシュボード（`/admin/dashboard`）
3. メニュー管理画面（`/admin/menu`）- 管理者のみ
4. 売上管理画面（`/admin/sales`）- 管理者のみ
5. ユーザー管理画面（`/admin/users`）- 管理者のみ

---

## 4. URL設計

### 4.1 顧客向けURL
- `GET /order?table=<id>` - セッション開始
- `POST /order/session/create` - セッション作成API
- `GET /order/menu` - メニュー一覧
- `POST /order/submit` - 注文送信API
- `GET /order/history` - 注文履歴
- `GET /order/call-staff` - 店員呼び出し画面
- `POST /order/call-staff` - 店員呼び出しAPI
- `GET /order/payment` - 会計画面
- `GET /api/order/status` - 注文ステータス取得API（リロード用）

### 4.2 管理画面URL
- `GET /admin/login` - ログイン画面
- `POST /admin/login` - ログイン処理
- `GET /admin/logout` - ログアウト
- `GET /admin/dashboard` - ダッシュボード
- `POST /admin/order/update-status` - 注文ステータス更新API
- `POST /admin/staff-call/resolve` - 呼び出し対応済みAPI
- `GET /admin/receipt/<session_id>` - レシート印刷
- `GET /admin/menu` - メニュー管理（管理者のみ）
- `POST /admin/menu/create` - メニュー追加API
- `POST /admin/menu/update/<id>` - メニュー更新API
- `POST /admin/menu/delete/<id>` - メニュー削除API
- `GET /admin/sales` - 売上管理（管理者のみ）
- `GET /admin/users` - ユーザー管理（管理者のみ）
- `POST /admin/users/create` - ユーザー作成API
- `POST /admin/users/update/<id>` - ユーザー更新API
- `POST /admin/users/delete/<id>` - ユーザー削除API

---

## 5. 技術スタック

### 5.1 バックエンド
- Python 3.x
- Django 4.x
- SQLite3

### 5.2 フロントエンド
- HTML5
- CSS3 (Bootstrap 5)
- JavaScript (Vanilla JS)

### 5.3 画像処理
- Pillow (画像リサイズ)

### 5.4 その他
- Django Admin（初期データ登録用）
- QRコード生成（管理コマンド）

---

## 6. ディレクトリ構成

```
mobileOrderDjango/
├── manage.py
├── requirements.txt
├── mobile_order/          # プロジェクト設定
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── order/                 # 注文アプリ
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── templates/
│       └── order/
│           ├── start_session.html
│           ├── menu.html
│           ├── history.html
│           ├── call_staff.html
│           └── payment.html
├── management_app/        # 管理アプリ
│   ├── migrations/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── decorators.py     # 権限チェック
│   └── templates/
│       └── management/
│           ├── login.html
│           ├── dashboard.html
│           ├── menu_management.html
│           ├── sales.html
│           └── users.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/                 # アップロード画像
    ├── menu/
    │   ├── original/
    │   ├── large/
    │   └── thumbnail/
```

---

## 7. 初期データ仕様

### 7.1 テーブル（10卓）
- テーブル番号: 1-10
- 座席数: 各4席（固定）
- QR URL: `/order?table=1` ～ `/order?table=10`

### 7.2 管理者ユーザー
- username: `admin`
- password: `admin123`
- role: `ADMIN`

### 7.3 スタッフユーザー
- username: `staff`
- password: `staff123`
- role: `STAFF`

### 7.4 サンプル商品（8商品）
1. ハンバーグステーキ - 1,200円
2. カルボナーラ - 980円
3. シーザーサラダ - 680円
4. フライドポテト - 480円
5. マルゲリータピザ - 1,400円
6. ティラミス - 580円
7. アイスコーヒー - 380円
8. オレンジジュース - 350円

※商品画像はプレースホルダー画像を使用

---

## 8. 開発フェーズ

### Phase 1: 環境構築・モデル作成
- Djangoプロジェクト作成
- モデル定義
- マイグレーション実行
- 初期データ投入

### Phase 2: 顧客向け機能実装
- セッション管理
- メニュー表示・注文機能
- 注文履歴表示
- 店員呼び出し
- 会計画面

### Phase 3: 管理画面実装
- 認証・権限管理
- ダッシュボード（注文管理）
- メニュー管理
- 売上管理
- ユーザー管理

### Phase 4: テスト・調整
- 機能テスト
- UI/UX調整
- バグ修正

---

## 9. 非機能要件

### 9.1 パフォーマンス
- プロトタイプのため、最適化は最小限
- 同時アクセス: 10-20ユーザー程度を想定

### 9.2 セキュリティ
- Django標準のCSRF保護
- パスワードハッシュ化（Django標準）
- 管理画面は認証必須

### 9.3 ブラウザ対応
- 顧客向け: モバイルブラウザ（Chrome, Safari最新版）
- 管理画面: デスクトップブラウザ（Chrome, Edge最新版）
