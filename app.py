import streamlit as st
import pandas as pd
import plotly.express as px
import time
import datetime
import os
from utils.database import get_database
from scheduler import tasks
from tests.yahoo.yahoo_news import scrape_yahoo_news
# タイトルを表示
st.title('Webスクレイピングダッシュボード')

# サイドバーにメニューを追加
menu = st.sidebar.selectbox("メニュー", ["データの可視化", "システム監視", "スクレイピング実行"])

if menu == "データの可視化":
    st.header("データの可視化")

    # データベースからデータを取得
    db = get_database()
    collection_name = st.selectbox("コレクションを選択", db.list_collection_names())
    collection = db[collection_name]
    data = list(collection.find())

    if data:
        df = pd.DataFrame(data)

        # 日付データの整形と追加
        df['time'] = pd.to_datetime(df['time'])
        df['date'] = df['time'].dt.date


        # 記事数の表示期間選択
        st.subheader("記事数")
        period = st.selectbox("表示期間", ["1日", "1週間", "1ヶ月"])

        # 期間に応じたデータのフィルタリング
        if period == "1日":
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=1)
        elif period == "1週間":
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(weeks=1)
        elif period == "1ヶ月":
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)

        filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]


        # 日毎の記事数を集計
        daily_counts = filtered_df.groupby('date').size().reset_index(name='count')

        # 折れ線グラフで表示
        fig = px.line(daily_counts, x='date', y='count', title=f'{period}の記事数')
        fig.update_xaxes(title_text="日付")
        fig.update_yaxes(title_text="記事数")
        st.plotly_chart(fig)

    else:
        st.info("データがありません。")

elif menu == "スクレイピング実行": # 新しいメニューを追加
    st.header("スクレイピング実行")

    if st.button("Yahoo!ニュースをスクレイピング"): # ボタンを追加
        with st.spinner('スクレイピング実行中...'):
            try:
                scrape_yahoo_news()
                st.success('スクレイピング完了！')
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

elif menu == "システム監視":
    st.header("システム監視")

    # ログファイルを読み込み、表示
    st.subheader("スクレイピング実行ログ")
    log_file_path = os.environ.get("LOG_FILE", "application.log") # config.pyと同じ設定
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as f: # エンコーディング指定
            log_content = f.read()
        st.text_area("ログ", log_content, height=300)

    # タスクの実行状況を表示
    st.subheader("スクレイピング実行状況")
    last_run = st.empty()  # 実行時間表示領域を確保
    next_run = st.empty()  # 次回実行時間表示領域を確保
    status = st.empty()  # ステータス表示領域を確保

    while True:
        # scheduler/tasks.py の next_run_time と run_status を取得
        try:
            now = datetime.datetime.now()
            next_run_time = tasks.next_run_time
            run_status = tasks.run_status

            last_run.text(f"最終実行時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            next_run.text(f"次回実行時間: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            status.text(f"ステータス: {run_status}")

        except Exception as e:
            st.error(f"タスクの実行状況の取得に失敗しました: {e}")

        time.sleep(60) # 60秒ごとに更新

