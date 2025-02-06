import streamlit as st


# タイトルを表示
st.title('私の初めてのStreamlitアプリ')

# テキストを表示
st.write('これはStreamlitのサンプルアプリです。')

# スライダーを表示
value = st.slider('値を選択してください', 0, 100, 50)

# 選択された値を表示
st.write(f'選択された値: {value}')