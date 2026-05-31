// FastAPI サーバーのベースURL(ローカル想定)
const API_BASE = "";

const form = document.getElementById("contact-form");
const result = document.getElementById("result");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  // 入力値の取得
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const message = document.getElementById("message").value.trim();

  // 簡易的なクライアント側チェック
  if (!name || !email || !message) {
    showResult("すべての項目を入力してください。", "error");
    return;
  }

  showResult("送信中...", "");

  try {
    const response = await fetch(`${API_BASE}/api/contact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, message }),
    });

    const data = await response.json();

    if (response.ok && data.success) {
      showResult(data.message, "success");
      form.reset();
    } else {
      // サーバーがエラー(バリデーション等)を返した場合
      showResult(data.message || "送信に失敗しました。", "error");
    }
  } catch (error) {
    // FastAPI サーバーが起動していない/接続できない場合など
    showResult(
      "サーバーに接続できませんでした。サーバーが起動しているか確認してください。",
      "error"
    );
  }
});

function showResult(text, type) {
  result.textContent = text;
  result.className = "result" + (type ? " " + type : "");
}
