import streamlit as st
import requests

st.set_page_config(page_title="Summary + Quiz", page_icon="📝", layout="centered")

st.title("📝 作業/文章摘要＋重點整理＋小考題")
st.caption("貼上文字 → 產生重點 5 點＋一句總結＋可能考題 3 題（免金鑰，使用本機 Ollama）。")

with st.sidebar:
    st.header("⚙️ 設定")
    model = st.text_input("Ollama 模型名稱", value="llama3.2:3b")
    lang = st.selectbox("輸出語言", ["繁體中文", "English"], index=0)

text = st.text_area("📄 貼上內容", height=260, placeholder="把教材、筆記或文章貼在這裡…")

def ollama_generate(model_name: str, prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {"model": model_name, "prompt": prompt, "stream": False}
    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()
    return r.json().get("response", "")

def build_prompt(user_text: str, language: str) -> str:
    lang_rule = "使用繁體中文回答。" if language == "繁體中文" else "Answer in English."
    return f"""
你是一位清楚且嚴謹的助教。{lang_rule}

請只根據使用者提供的內容輸出以下三個區塊（Markdown 格式，標題必須一致）：

## 1) 重點（5 點）
- 只列 5 點，句子短、資訊密度高。

## 2) 一句總結（1 句）
- 用 1 句話總結全文核心。

## 3) 可能考題（3 題，含答案與解析）
- 每題格式固定：
Q1. 題目
A1. 答案
解析：2–3 句（說明答案為何正確，必須能從內容推得出來）

限制：
- 不要捏造內容沒有的資訊。
- 若內容不足以出題，請在「可能考題」區塊開頭加：⚠️ 內容不足，建議補充哪些資訊（列 2 點）。

使用者內容如下：
\"\"\"\n{user_text}\n\"\"\"
""".strip()

if st.button("🚀 生成", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("你還沒貼內容喔～先貼一段文字再按生成。")
        st.stop()

    prompt = build_prompt(text.strip(), lang)

    try:
        with st.spinner("本機模型生成中…（第一次可能較慢）"):
            output = ollama_generate(model, prompt)
        st.success("完成 ✅")
        st.markdown(output)
    except Exception as e:
        st.error("呼叫本機模型失敗。請確認：1) Ollama 有安裝 2) 模型有 pull 3) Ollama 有在背景跑")
        st.code(str(e), language="text")
