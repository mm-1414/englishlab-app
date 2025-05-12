import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import openai

# --- OpenAI APIキーを環境変数から取得 ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Googleサービスアカウント認証情報を環境変数から取得 ---
service_account_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)

# --- Googleスプレッドシートに接続(シート名は必要に応じて変更) ---
worksheet = gc.open("englishlab-log").sheet1  # シート名が違う場合は変更してください

# --- Streamlit アプリUI ---
st.title("英作文 採点アプリ")

code_input = st.text_input("使用コードを入力してください")
code_verified = True  # 今は常に正しいと仮定

if code_verified:
    name = st.text_input("あなたの名前を入力してください")

    if name:
        st.markdown("英作文とお題を入力してください。")
        prompt = st.text_area("お題 (例: Do the benefits of online shopping outweigh the disadvantages?)")
        user_essay = st.text_area("あなたの英作文")

        if st.button("採点を開始する"):
            if prompt and user_essay:
                with st.spinner("採点中..."):

                    # OpenAI API による採点処理
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an English teacher. Score the essay from 1 to 10 based on grammar, coherence, and content. Then explain the score in Japanese (です・ます調)."},
                            {"role": "user", "content": f"お題: {prompt}\n英作文: {user_essay}"}
                        ]
                    )

                    result = response.choices[0].message.content.strip()
                    st.success("採点完了!")
                    st.text_area("添削結果", result, height=400)

                    # --- ログをスプレッドシートに記録 ---
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    worksheet.append_row([timestamp, name, prompt, user_essay, result])
            else:
                st.warning("お題と英作文の両方を入力してください。")
