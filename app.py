import streamlit as st
from pathlib import Path
from PIL import Image
import datetime

# ========= 基本設定 =========
st.set_page_config(page_title="Eddie 小餐廳點餐系統", layout="wide")

APP_DIR = Path(__file__).parent
IMG_DIR = APP_DIR / "images"

VERSION = "v2-img-debug"  # 方便你辨識現在跑的是不是新版

MENU = {
    "牛肉麵 🍜": {"price": 120, "img": "beef-noodle.jpg", "desc": "搭配手工製作的好味道 ✨"},
    "滷肉飯 🍚": {"price": 80, "img": "braised-pork-rice.jpg", "desc": "經典台灣小吃 🇹🇼"},
    "珍珠奶茶 🥤": {"price": 60, "img": "bubble-tea.jpg", "desc": "最受歡迎的飲料 👑"},
}

if "cart" not in st.session_state:
    st.session_state.cart = {}
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None

st.markdown(f"**目前程式版本：{VERSION}**")  # <- 看到這行就是新版

# ========= 左右版面 =========
col1, col2 = st.columns([2, 3])

# ========= 左側：菜單 =========
with col1:
    st.title("🍴 今日菜單")
    for name, info in MENU.items():
        st.subheader(f"{name} — {info['price']} 元")
        img_path = IMG_DIR / info["img"]
        if img_path.exists():
            try:
                # 兩種方式擇一；保險起見先用 PIL 再 fallback
                img = Image.open(img_path)
                st.image(img, width=260)
            except Exception as e:
                st.warning(f"⚠ 圖片載入失敗（PIL）：{img_path}\n{e}")
                st.image(str(img_path.resolve()), width=260)
        else:
            st.warning(f"⚠ 找不到圖片：{img_path}")
        st.caption(info["desc"])
        st.divider()

# ========= 右側：點餐 + 購物車 =========
with col2:
    st.title("🧾 我要點餐")

    item = st.selectbox("請選擇餐點", list(MENU.keys()))
    qty = st.number_input("數量", min_value=1, step=1, value=1)

    if st.button("➕ 加入購物車"):
        st.session_state.cart[item] = st.session_state.cart.get(item, 0) + qty
        st.success(f"已加入 {item} x {qty}")

    st.divider()
    st.subheader("🛒 購物車")

    if st.session_state.cart:
        total = 0
        for name, q in st.session_state.cart.items():
            price = MENU[name]["price"]
            total += price * q
            st.write(f"{name} x {q} = {price*q} 元")
        st.subheader(f"💰 總金額：{total} 元")

        if st.button("✅ 結帳"):
            receipt = {
                "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": st.session_state.cart.copy(),
                "total": total,
            }
            st.session_state.last_receipt = receipt
            st.session_state.cart.clear()
            st.success("結帳完成 ✅ 收據已產生")
    else:
        st.info("購物車是空的，先從左邊選餐點吧！")

    st.divider()
    st.subheader("🧾 收據")
    rec = st.session_state.last_receipt
    if rec:
        with st.expander("展開/收合收據", expanded=True):
            st.write(f"收據編號：{rec['id']}")
            st.write(f"時間：{rec['time']}")
            st.write("------")
            for name, q in rec["items"].items():
                price = MENU[name]["price"]
                st.write(f"- {name} x {q} (單價 {price} 元)")
            st.write(f"💰 總金額：{rec['total']} 元")
    else:
        st.caption("結帳後會顯示最新收據。")

# ========= 偵錯資訊（幫你確認雲端看到的檔案）=========
with st.expander("🔍 圖片偵錯資訊（只在你檢查時打開即可）", expanded=False):
    st.write("APP_DIR：", str(APP_DIR.resolve()))
    st.write("IMG_DIR：", str(IMG_DIR.resolve()))
    st.write("IMG_DIR.exists()：", IMG_DIR.exists())
    if IMG_DIR.exists():
        files = [p.name for p in IMG_DIR.iterdir()]
        st.write("images 目錄檔案：", files)

# ========= 頁尾 =========
st.caption("© Eddie demo — 若圖片未顯示，請確認 images/ 目錄與檔名是否正確，或在上方展開偵錯資訊。")
