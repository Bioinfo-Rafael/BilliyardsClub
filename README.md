# KLビリヤード部 サイト + FastAPI

ビリヤード部の紹介サイトです。静的なフロントエンド(HTML / CSS / JavaScript)と、バックエンドの FastAPI サーバーで構成されています。
自分の PC 上で動かし、Cloudflare Tunnel 経由で外部公開することを想定しています。

## ディレクトリ構成

```
my-site/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## 必要環境

- Python 3.9 以上
- (任意)Cloudflare Tunnel を使う場合は `cloudflared`

---

## 1. バックエンド(FastAPI)のセットアップと起動

### 1-1. Python 仮想環境の作成

```bash
cd backend
python -m venv .venv
```

### 1-2. 仮想環境の有効化

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 1-3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 1-4. サーバーの起動

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

起動後、以下で動作確認できます。

- ブラウザ: http://localhost:8000
- Swagger UI(自動生成ドキュメント): http://localhost:8000/docs

---

## 2. フロントエンドの起動

フロントエンドはビルド不要の静的ファイルです。簡易 HTTP サーバーで配信します。
(`file://` で直接開くと CORS で API を叩けないため、HTTP サーバー経由を推奨します。)

別のターミナルを開いて、`frontend` ディレクトリで以下のいずれかを実行します。

### Python の簡易サーバーを使う場合(ポート 8080)

```bash
cd frontend
python -m http.server 8080
```

→ ブラウザで http://localhost:8080 を開く

### VS Code の Live Server を使う場合(ポート 5500)

`frontend/index.html` を Live Server で開きます(デフォルトで http://127.0.0.1:5500)。

> どちらのポート(5500 / 8080)も、バックエンドの CORS 設定で許可済みです。

---

## 3. ブラウザで確認する URL

| 内容 | URL |
| --- | --- |
| フロントエンド(http.server) | http://localhost:8080 |
| フロントエンド(Live Server) | http://127.0.0.1:5500 |
| バックエンド動作確認 | http://localhost:8000 |
| API ドキュメント | http://localhost:8000/docs |

---

## 4. API の動作確認

サーバー起動後、`curl` で確認できます。

### 動作確認用

```bash
curl http://localhost:8000/
# => {"message":"FastAPI server is running"}
```

### ヘルスチェック

```bash
curl http://localhost:8000/api/health
# => {"status":"ok"}
```

### お問い合わせ(正常時)

```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"山田太郎","email":"taro@example.com","message":"テストです"}'
# => {"success":true,"message":"お問い合わせを受け付けました"}
```

### お問い合わせ(未入力でエラー)

```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"","email":"","message":""}'
# => {"success":false,"message":"name, email, message はすべて必須です"} (HTTP 400)
```

ブラウザの場合は、http://localhost:8080 のお問い合わせフォームから送信すると、
API の結果が画面に表示されます。サーバーが起動していない場合はエラーメッセージが表示されます。

---

## 5. CORS について

`backend/main.py` では、開発用に以下のオリジンからのアクセスを許可しています。

- http://localhost:5500
- http://127.0.0.1:5500
- http://localhost:8080
- http://127.0.0.1:8080

> **本番公開時の注意**
> 一時的に全許可したい場合は `allow_origins=["*"]` にもできますが、
> **本番(Cloudflare Tunnel などで外部公開する場合)は、公開ドメインのみに限定してください。**
> `["*"]` のまま公開すると、どのサイトからでも API を叩けてしまいます。

---

## 6. Cloudflare Tunnel で公開する場合の例

`cloudflared` を使うと、ローカルのサーバーを一時的に外部公開できます。

### 6-1. インストール(macOS / Homebrew の例)

```bash
brew install cloudflared
```

### 6-2. クイックトンネル(お試し・ログイン不要)

FastAPI サーバー(ポート 8000)を起動した状態で:

```bash
cloudflared tunnel --url http://localhost:8000
```

実行すると `https://xxxx-xxxx.trycloudflare.com` のような一時 URL が払い出されます。

> フロントエンド(8080)も公開したい場合は、フロントエンド用に別のトンネルを立てるか、
> フロントエンドの `script.js` の `API_BASE` を、公開された API の URL に書き換えてください。

### 6-3. 名前付きトンネル(独自ドメインで継続運用する場合)

```bash
# Cloudflare アカウントにログイン
cloudflared tunnel login

# トンネルを作成
cloudflared tunnel create my-site

# 設定ファイル(~/.cloudflared/config.yml)で
# ホスト名とローカルのポート(localhost:8000 など)を紐付け、ルーティングを設定して起動
cloudflared tunnel run my-site
```

詳細は Cloudflare の公式ドキュメントを参照してください。

> **公開時のチェックリスト**
> - CORS の `allow_origins` を公開ドメインに限定する
> - 不要なエンドポイントを公開しない
> - 必要に応じて認証・レート制限を追加する
