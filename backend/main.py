from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="KL Billiards Club API")

# CORS設定
# 開発時はローカルのフロントエンド用オリジンを許可しています。
# 本番公開時(Cloudflare Tunnel経由など)は、公開ドメインのみに制限してください。
# 一時的に全許可したい場合は allow_origins=["*"] に置き換えられますが、
# 本番では必ず具体的なオリジンに限定してください(README参照)。
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactForm(BaseModel):
    name: str = ""
    email: str = ""
    message: str = ""


@app.get("/")
def root():
    """動作確認用エンドポイント"""
    return {"message": "FastAPI server is running"}


@app.get("/api/health")
def health():
    """ヘルスチェック用エンドポイント"""
    return {"status": "ok"}


@app.post("/api/contact")
def contact(form: ContactForm):
    """お問い合わせフォーム受付用エンドポイント"""
    # 未入力チェック(前後の空白のみも未入力扱い)
    if not form.name.strip() or not form.email.strip() or not form.message.strip():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "name, email, message はすべて必須です",
            },
        )

    # データ保存やメール送信は行いません。
    return {"success": True, "message": "お問い合わせを受け付けました"}
