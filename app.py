import streamlit as st
from pathlib import Path

# 頁面設定
st.set_page_config(page_title="Eddie 小餐廳點餐系統", page_icon="🍜", layout="wide")

# 圖片路徑
IMG_DIR = Path("images")

# 菜單
MENU = {
    "牛肉麵": {"price": 120, "img": IMG_DIR / "beef-noodle.jpg"},
    "滷肉飯": {"price": 80, "img": IMG_DIR / "braised-pork-rice.jpg"},
    "珍珠奶茶": {"price": 60, "img": IMG_DIR / "bubble-tea.jpg"}
}

# 初始化購物車
if "cart" not in st.session_state:
    st.session_state.cart = {}

st.title("Eddie 小餐廳點餐系統")
st.caption("快速下單 · 即時小計 · 可離線本機使用")

# 今日菜單
st.header("今日菜單")
for name, data in MENU.items():
    st.image(data["img"], width=200)
    st.write(f"**{name}** - {data['price']} 元")

# 點餐區
st.header("我要點餐")
item = st.selectbox("請選擇餐點", list(MENU.keys()))
qty = st.number_input("數量", 1, 10, 1)

if st.button("➕ 加入購物車"):
    st.session_state.cart[item] = st.session_state.cart.get(item, 0) + qty
    st.success(f"已加入 {item} x {qty}")

# 購物車
st.header("🛒 購物車")
if st.session_state.cart:
    total = 0
    for name, q in st.session_state.cart.items():
        price = MENU[name]["price"] * q
        total += price
        st.write(f"{name} x {q} = {price} 元")
    st.subheader(f"💰 總金額：{total} 元")
else:
    st.info("購物車是空的，先從左邊選餐點吧！")
