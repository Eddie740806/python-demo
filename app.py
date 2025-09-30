# app.py
import streamlit as st
from pathlib import Path
from datetime import datetime

# ================== 基本設定 ==================
st.set_page_config(page_title="Eddie 小餐廳點餐系統", layout="wide")
VERSION = "v2.2 (img+cart+receipt)"

BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "images"

# ================== 菜單 (只放檔名，路徑由程式組出) ==================
MENU = {
    "牛肉麵 🍜": {
        "price": 120,
        "img": "beef-noodle.jpg",
        "desc": "搭配手工製作的好味道 ✨",
    },
    "滷肉飯 🍚": {
        "price": 80,
        "img": "braised-pork-rice.jpg",
        "desc": "經典台灣小吃 ❤️",
    },
    "珍珠奶茶 🧋": {
        "price": 60,
        "img": "bubble-tea.jpg",
        "desc": "最受歡迎的飲料 🥤",
    },
}

# ================== Session 初始化 ==================
if "cart" not in st.session_state:
    st.session_state.cart = {}        # {"品名": 數量}
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None
if "receipts" not in st.session_state:
    st.session_state.receipts = []    # 收據歷史

# ================== 小工具函式 ==================
def add_to_cart(item_name: str, qty: int):
    if qty <= 0:
        return
    st.session_state.cart[item_name] = st.session_state.cart.get(item_name, 0) + qty

def clear_cart():
    st.session_state.cart = {}

def calc_total(cart: dict) -> int:
    return sum(MENU[name]["price"] * q for name, q in cart.items())

def checkout():
    if not st.session_state.cart:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receipt = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "time": now,
        "items": st.session_state.cart.copy(),
        "total": calc_total(st.session_state.cart),
    }
    st.session_state.last_receipt = receipt
    st.session_state.receipts.append(receipt)
    clear_cart()

# ================== 版面 ==================
st.markdown(f"**⚡ 目前程式版本：{VERSION}**")

left, right = st.columns([2, 3])

# ================== 左欄：今日菜單 ==================
with left:
    st.title("🍽️ 今日菜單")

    # 把菜名、圖片、價格排版顯示
    for name, item in MENU.items():
        img_path = IMG_DIR / item["img"]
        with st.container(border=True):
            cols = st.columns([1, 3])
            with cols[0]:
                # 圖片：若雲端成功推上 GitHub，這裡就能看到
                st.image(str(img_path), use_column_width=True)
            with cols[1]:
                st.subheader(f"{name} — {item['price']} 元")
                st.caption(item["desc"])

    st.divider()

    st.subheader("🧾 我要點餐")
    c1, c2 = st.columns([3, 2])

    with c1:
        dish = st.selectbox("請選擇餐點", list(MENU.keys()), index=0)

    with c2:
        # 數量：使用 number_input，避免版本差造成按鈕 callback 亂跑
        qty = st.number_input("數量", min_value=1, max_value=99, value=1, step=1)

    if st.button("➕ 加入購物車", use_container_width=False):
        add_to_cart(dish, int(qty))
        st.success(f"已加入 {dish} × {qty}")

# ================== 右欄：購物車 + 收據 ==================
with right:
    st.title("🛒 購物車")

    if not st.session_state.cart:
        st.info("購物車是空的，先從左邊選餐點吧！", icon="ℹ️")
    else:
        total = calc_total(st.session_state.cart)
        # 顯示購物車每一項
        for name, q in st.session_state.cart.items():
            price = MENU[name]["price"]
            line = f"{name} × {q}  （單價 {price} 元）  小計 {price*q} 元"
            st.write("- " + line)
        st.subheader(f"💰 總金額：{total} 元")

        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("✅ 結帳", type="primary"):
                checkout()
                st.success("結帳完成！收據已產生於下方『收據』區塊。")
        with cc2:
            if st.button("🗑️ 清空購物車"):
                clear_cart()
                st.info("購物車已清空。")

    st.divider()
    st.subheader("🧾 收據")

    # 最近一張收據（可收合）
    with st.expander("📄 展開/收合『最近一張收據』", expanded=False):
        rec = st.session_state.last_receipt
        if not rec:
            st.caption("目前尚無最近收據。")
        else:
            st.write(f"收據編號：**{rec['id']}**")
            st.write(f"時間：**{rec['time']}**")
            for name, q in rec["items"].items():
                st.write(f"• {name} × {q}  （單價 {MENU[name]['price']} 元）")
            st.write(f"**總金額：{rec['total']} 元**")

    # 收據歷史（如不需要可移除）
    with st.expander("🗂️ 收據歷史", expanded=False):
        if not st.session_state.receipts:
            st.caption("尚無歷史收據。")
        else:
            for i, r in enumerate(reversed(st.session_state.receipts), start=1):
                st.markdown(f"**第 {i} 筆**｜收據編號：`{r['id']}`｜時間：`{r['time']}`｜總金額：`{r['total']}` 元")
                with st.container():
                    for name, q in r["items"].items():
                        st.write(f"　• {name} × {q}  （單價 {MENU[name]['price']} 元）")
                st.divider()

    st.caption("© Eddie demo．若圖片未顯示，請確認 `images/` 目錄與檔名是否正確。")
