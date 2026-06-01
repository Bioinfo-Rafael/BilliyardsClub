from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="KL Billiards Club API")

# CORS設定
# 外部公開ドメインやLAN内、どこからアクセスされてもエラーにならないように全許可にします
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactForm(BaseModel):
    name: str = ""
    email: str = ""
    message: str = ""

# メール送信用の設定
SMTP_SERVER = "smtp.gmail.com"          # Gmailを指定
SMTP_PORT = 587                         # TLSポート
SENDER_EMAIL = "tohokupoolserver@gmail.com"   # 送信元のメールアドレス
SENDER_PASSWORD = "ijst rryp hxaz zlmk" # Googleの「アプリパスワード（16桁）」
RECEIVER_EMAIL = ["marimo.sanai@gmail.com",""] # お問い合わせの通知を受け取りたいメールアドレス、鈴木先輩のアドレスを入れてください！！

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
    """お問い合わせフォーム受付 ＆ メール送信"""
    # 未入力チェック
    if not form.name.strip() or not form.email.strip() or not form.message.strip():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "name, email, message はすべて必須です",
            },
        )

    # ここからメール送信処理を追加
    try:
        # メールの枠組みを作成
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECEIVER_EMAIL)
        msg['Subject'] = f"【ホームページお問い合わせ】{form.name}様より"

        # メールの本文を組み立て
        body = f"""
        ホームページから新しいお問い合わせが届きました。

        【お名前】
        {form.name}

        【メールアドレス】
        {form.email}

        【メッセージ内容】
        {form.message}
        """
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # SMTPサーバーに接続してメールを送信
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # 安全な通信を開始
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        return {"success": True, "message": "お問い合わせメールを送信しました"}

    except Exception as e:
        # 万が一エラーが起きた場合はログに出力し、フロントにもエラーを返す
        print(f"Mail sending error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"メール送信に失敗しました: {e}",
            },
        )

# Dockerコンテナ内で、ポート8000番で常駐起動させるための命令
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
