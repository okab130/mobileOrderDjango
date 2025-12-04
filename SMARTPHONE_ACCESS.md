# スマホからのアクセス設定ガイド（ngrok経由）

このガイドでは、ngrokを使用してスマホからアクセスする方法を説明します。

## 前提条件

- 開発サーバーが起動できる状態であること
- インターネット接続があること
- スマホがインターネットに接続されていること（Wi-Fiまたはモバイルデータ）

---

## セットアップ手順

### 1. ngrokのインストールと設定

#### 1-1. アカウント作成
1. https://ngrok.com/ にアクセス
2. 「Sign up」から無料アカウントを作成

#### 1-2. ngrokのダウンロード
1. ログイン後、「Download」ページから環境に合わせてダウンロード
   - Windows: ngrok-v3-stable-windows-amd64.zip
   - macOS: ngrok-v3-stable-darwin-amd64.zip
   - Linux: ngrok-v3-stable-linux-amd64.tgz

2. ダウンロードしたファイルを解凍
3. 実行ファイルをパスの通った場所に配置（任意）

#### 1-3. 認証トークンの設定（初回のみ）
1. ngrokダッシュボードの「Your Authtoken」からトークンをコピー
2. 以下のコマンドで設定：
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

### 2. Djangoサーバーの起動

```bash
# 仮想環境を有効化
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# サーバー起動
python manage.py runserver
```

### 3. ngrokでトンネル作成（別ターミナル）

新しいターミナル（コマンドプロンプト）を開いて以下を実行：

```bash
ngrok http 8000
```

以下のような画面が表示されます：

```
ngrok

Session Status                online
Account                       yourname@example.com (Plan: Free)
Version                       3.x.x
Region                        Japan (jp)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xx-xx-xxx-xxx.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**重要:** `Forwarding` の `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app` をコピーしてください。

### 4. Django設定の変更

`mobile_order/settings.py` を開いて以下を編集：

```python
# ALLOWED_HOSTSを変更
ALLOWED_HOSTS = ['xxxx-xx-xx-xxx-xxx.ngrok-free.app', 'localhost', '127.0.0.1']

# CSRF_TRUSTED_ORIGINSを追加（ファイル末尾に追加）
CSRF_TRUSTED_ORIGINS = ['https://xxxx-xx-xx-xxx-xxx.ngrok-free.app']
```

**注意:** `xxxx-xx-xx-xxx-xxx` の部分は、ngrokで表示された実際のURLに置き換えてください。

### 5. Djangoサーバーの再起動

設定を変更したら、サーバーを再起動します：

```bash
# サーバーが起動しているターミナルで Ctrl+C を押して停止
# 再度起動
python manage.py runserver
```

### 6. スマホからアクセス

スマホのブラウザで以下のURLにアクセス：

- **顧客画面（テーブル1）:**  
  `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app/order?table=1`

- **管理画面:**  
  `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app/management/login/`

**注意:** ngrokの無料版では、初回アクセス時にngrokの警告ページが表示されます。「Visit Site」ボタンをクリックして続行してください。

---

## QRコード生成（オプション）

テーブルごとにQRコードを生成しておくと便利です。

### QRコード生成サイト
- https://www.qrcode-monkey.com/
- https://www.the-qrcode-generator.com/

### 生成するURL例
- テーブル1: `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app/order?table=1`
- テーブル2: `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app/order?table=2`
- ...
- テーブル10: `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app/order?table=10`

生成したQRコードを印刷して、各テーブルに設置します。

---

## トラブルシューティング

### ngrokのURLにアクセスできない

**確認1: ALLOWED_HOSTSとCSRF設定**
- `settings.py`にngrokのURLが正しく設定されているか確認
- `CSRF_TRUSTED_ORIGINS`に`https://`が含まれているか確認
- スペルミスがないか確認

**確認2: サーバーの再起動**
- `settings.py`を変更した後、必ずサーバーを再起動

**確認3: ngrokのトンネルが有効か**
- ngrokのターミナルで「Session Status: online」と表示されているか確認

### ngrokのURLが変わってしまう

ngrok無料版では、トンネルを作り直すたびにURLが変わります。

**対処法:**
1. ngrokを再起動したら、新しいURLを確認
2. `settings.py`を新しいURLで更新
3. サーバーを再起動
4. QRコードを作り直す（必要な場合）

**固定URLを使いたい場合:**
- ngrokの有料プラン（Basic以上）で固定ドメインを取得

### CSRFエラーが出る

```
CSRF verification failed. Request aborted.
```

**対処法:**
1. `settings.py`の`CSRF_TRUSTED_ORIGINS`にngrok URLが設定されているか確認
2. https://（スキーム）が含まれているか確認
   ```python
   CSRF_TRUSTED_ORIGINS = ['https://xxxx-xx-xx-xxx-xxx.ngrok-free.app']
   ```
3. サーバーを再起動

### 「Invalid Host header」エラー

**対処法:**
1. `settings.py`の`ALLOWED_HOSTS`にngrok URLが設定されているか確認
   ```python
   ALLOWED_HOSTS = ['xxxx-xx-xx-xxx-xxx.ngrok-free.app', 'localhost', '127.0.0.1']
   ```
2. サーバーを再起動

### ngrokの警告ページが毎回表示される

ngrok無料版の仕様です。「Visit Site」をクリックすれば使用できます。

警告を回避したい場合はngrokの有料プランを検討してください。

---

## ngrokの便利な機能

### Web Interface（トラフィック確認）

ngrok起動中に `http://127.0.0.1:4040` にアクセスすると、リクエストとレスポンスの詳細を確認できます。デバッグに便利です。

### トンネルの停止

ngrokを停止するには、ngrokを実行しているターミナルで `Ctrl+C` を押します。

---

## セキュリティ上の注意

- ngrokは開発・テスト用途のみで使用してください
- このシステムはプロトタイプであり、本番環境での使用は想定していません
- 重要なデータや個人情報は扱わないでください
- ngrokのURLは公開されるため、URLを知っている人は誰でもアクセスできます
- 使用しない時はngrokとサーバーを停止してください

---

## まとめ

1. ngrokをインストール・認証
2. Djangoサーバーを起動
3. ngrokでトンネル作成
4. settings.pyにngrok URLを設定
5. サーバー再起動
6. スマホからアクセス

これで、どこからでもスマホでシステムにアクセスできます！
