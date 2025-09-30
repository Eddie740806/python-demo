# app.py
# -*- coding: utf-8 -*-

import time
from datetime import datetime
from pathlib import Path
import streamlit as st


# ----------------------------
# 基本設定
# ----------------------------
st.set_page_config(
    page_title="Eddie 小餐廳點餐系統",
    page_icon="🍜",
    layout="wide",
)

IMG_DIR = Path("images")

# 菜單（記得 images/ 下要有這三張圖片）
MENU = {
    "牛肉麵": {"price": 120, "img": str(IMG_DIR / "beef-noodle.jpg")},
    "滷肉飯": {"price": 80,  "img": str(IMG_DIR / "braised-pork-rice.jpg")},
    "珍珠奶茶": {"price": 60, "img": str(IMG_DIR / "bubble-tea.jpg")},
}


# ----------------------------
# Session State 初始化
# ----------------------------
if "cart" not in st.session_state:
    # 購物車：{品名: 數量}
    st.session_state.cart = {}

if "last_receipt" not in st.session_state:
    # 最近一次結帳的收據（顯示在頁面下方）
    st.session_state.last_receipt = None

if "history" not in st.session_state:
    # 所有收據歷史（最新放最前）
    st.session_state.history = []


# ----------------------------
# 小工具
# ----------------------------
def add_to_cart(item: str, qty: int):
    """加入購物車"""
    if qty <= 0:
        return
    st.session_state.cart[item] = st.session_state.cart.get(item, 0) + qty


def remove_one(item: str):
    """購物車移除單一數量"""
    if item in st.session_state.cart:
        st.session_state.cart[item] -= 1
        if st.session_state.cart[item] <= 0:
            del st.session_state.cart[item]


def clear_cart():
    st.session_state.cart = {}


def calc_total() -> int:
    """計算購物車總金額"""
    total = 0
    for name, q in st.session_state.cart.items():
        total += MENU[name]["price"] * q
    return total


def checkout():
    """結帳：建立收據、清空購物車、更新歷史"""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    receipt = {
        "id": ts,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": {k: v for k, v in st.session_state.cart.items()},
        "total": calc_total(),
    }
    # 更新 session 中的收據/歷史
    st.session_state.last_receipt = receipt
    st.session_state.history.insert(0, receipt)

    # 清空購物車
    clear_cart()

    st.success("結帳成功 ✅ 已產生收據！")
    time.sleep(0.6)
    st.rerun()


# ----------------------------
# 樣式（可自行微調）
# ----------------------------
st.markdown(
    """
    <style>
    .stButton>button {
        border-radius: 12px;
        height: 38px;
        padding: 0 16px;
    }
    .menu-card {
        padding: 14px 16px;
        border: 1px solid #eee;
        border-radius: 14px;
        margin-bottom: 14px;
        background: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------
# 版面：兩欄
# ----------------------------
left, right = st.columns([1.1, 1])

with left:
    st.header("🍽️ 今日菜單")

    # 逐品項顯示，左圖右字（圖片寬 250px）
    for name, meta in MENU.items():
        with st.container():
            st.markdown('<div class="menu-card">', unsafe_allow_html=True)

            col_img, col_text = st.columns([1, 2])
            with col_img:
                st.image(meta["img"], width=250)

            with col_text:
                st.subheader(f"{name} — {meta['price']} 元")
                st.caption("搭配手工製作的好味道 ✨")

            st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.header("🧾 我的點餐")

    # 點餐操作：選擇餐點 + 數量 + 加入購物車
    cols = st.columns([3, 1])
    with cols[0]:
        picked = st.selectbox("請選擇餐點", list(MENU.keys()))
    with cols[1]:
        qty = st.number_input("數量", min_value=1, max_value=99, value=1, step=1)

    if st.button("➕ 加入購物車", use_container_width=True):
        add_to_cart(picked, qty)
        st.success(f"已加入 {picked} x {qty}")
        time.sleep(0.4)
        st.rerun()

    st.divider()

    # 購物車清單
    st.subheader("🛒 購物車")
    cart = st.session_state.cart

    if not cart:
        st.info("購物車是空的，先在上面選餐點吧！")
    else:
        total = 0
        for name, q in cart.items():
            price = MENU[name]["price"]
            line = price * q
            total += line

            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                st.write(f"**{name}**")
            with c2:
                st.write(f"單價：{price} 元")
            with c3:
                st.write(f"數量：{q}")
            with c4:
                if st.button("➖ 移除 1", key=f"rm_{name}"):
                    remove_one(name)
                    st.rerun()

        st.markdown(f"### 💰 總金額：**{total} 元**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🧹 清空購物車", use_container_width=True):
                clear_cart()
                st.rerun()
        with c2:
            if st.button("✅ 結帳", use_container_width=True):
                checkout()

    st.divider()

    # 收據區
    st.subheader("🧾 收據")
    rec = st.session_state.last_receipt
    with st.expander("展開/收合收據", expanded=True):
        if not rec:
            st.caption("目前尚無歷史收據。")
        else:
            st.write(f"收據編號：**{rec['id']}**")
            st.write(f"時間：**{rec['time']}**")

            st.write("---")
            for name, q in rec["items"].items():
                price = MENU[name]["price"]
                st.write(f"- **{name}** × **{q}**（單價 **{price} 元**）")
            st.write("---")
            st.write(f"**總金額：{rec['total']} 元**")


# 頁尾提醒
st.caption("© Eddie demo．若圖片未顯示，請確認 `images/` 目錄與檔名是否正確。")
