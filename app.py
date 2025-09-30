# app.py
import time
from pathlib import Path
from PIL import Image
import streamlit as st

# -------------------------
# 基本設定
# -------------------------
st.set_page_config(
    page_title="Eddie 小餐廳點餐系統",
    page_icon="🍜",
    layout="wide"
)

APP_DIR = Path(__file__).parent
IMG_DIR = APP_DIR / "images"
VERSION = "v2.2"

# -------------------------
# 菜單資料
# -------------------------
MENU = {
    "牛肉麵 🍜": {
        "price": 120,
        "img": "beef-noodle.jpg",
        "desc": "搭配手工製作的好味道 ✨"
    },
    "滷肉飯 🥣": {
        "price": 80,
        "img": "braised-pork-rice.jpg",
        "desc": "經典台灣小吃 ❤️"
    },
    "珍珠奶茶 🧋": {
        "price": 60,
        "img": "bubble-tea.jpg",
        "desc": "黑糖蜜漬的軟 Q 珍珠！"
    },
}

# -------------------------
# Session State 初始化
# -------------------------
if "cart" not in st.session_state:
    st.session_state.cart = {}            # {"牛肉麵 🍜": 數量, ...}
if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None  # 保存最後一次結帳資訊


# -------------------------
# 小工具函式
# -------------------------
def add_to_cart(item: str, qty: int = 1):
    """加入購物車"""
    if qty <= 0:
        return
    st.session_state.cart[item] = st.session_state.cart.get(item, 0) + qty


def calc_total(cart: dict) -> int:
    """計算總金額"""
    total = 0
    for name, q in cart.items():
        total += MENU[name]["price"] * q
    return total


def try_rerun():
    """相容不同 Streamlit 版本的重新整理"""
    try:
        st.rerun()  # 新版
    except Exception:
        try:
            st.experimental_rerun()  # 舊版
        except Exception:
            pass


def checkout():
    """結帳：產生收據、清空購物車"""
    if not st.session_state.cart:
        st.warning("購物車是空的，先點餐吧！")
        return

    # 產生收據資料
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    receipt = {
        "id": int(time.time()),
        "time": now,
        "items": st.session_state.cart.copy(),
        "total": calc_total(st.session_state.cart),
    }
    st.session_state.last_receipt = receipt
    st.session_state.cart = {}
    st.success("結帳成功！收據已產生 ✅")
    try_rerun()


def render_menu_card(name: str, item: dict):
    """左側菜單卡片（圖片在上，資訊在下）"""
    img_path = IMG_DIR / item["img"]

    with st.container(border=True):
        # 圖片
        if img_path.exists():
            st.image(str(img_path), use_container_width=True)
        else:
            st.warning(f"找不到圖片：{img_path.name}")

        # 名稱與價格
        st.markdown(f"### {name} — {item['price']} 元")
        if item.get("desc"):
            st.caption(item["desc"])

        # 加入購物車操作列
        c1, c2 = st.columns([3, 2])
        with c1:
            # 單品直接加入 1 份
            if st.button(f"➕ 加入購物車（{name}）", use_container_width=True, key=f"btn_add_{name}"):
                add_to_cart(name, 1)
                st.toast(f"已加入 {name} × 1")
                try_rerun()
        with c2:
            # 快速選取數量加入
            qty = st.number_input("數量", 1, 20, 1, key=f"qty_{name}", label_visibility="collapsed")
            if st.button("加入指定數量", use_container_width=True, key=f"btn_add_qty_{name}"):
                add_to_cart(name, int(qty))
                st.toast(f"已加入 {name} × {qty}")
                try_rerun()


# -------------------------
# 頁面上方資訊列
# -------------------------
st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:0.5rem;">
      <h2 style="margin:0;">Eddie 小餐廳點餐系統</h2>
      <span style="opacity:.6;">（{VERSION}）</span>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# 版面：左（菜單） / 右（購物車＋收據）
# -------------------------
left, right = st.columns([7, 5], gap="large")

# 左側：菜單卡片
with left:
    st.subheader("🍽️ 今日菜單")
    for pname, pdata in MENU.items():
        render_menu_card(pname, pdata)

# 右側：購物車與收據
with right:
    st.subheader("🛒 購物車")

    # 顯示購物車內容
    cart_box = st.container(border=True)
    with cart_box:
        if not st.session_state.cart:
            st.info("購物車是空的，先從左邊選餐點吧！")
        else:
            # 表格列出項目
            for name, q in st.session_state.cart.items():
                price = MENU[name]["price"]
                row = st.columns([5, 3, 2, 2])
                with row[0]:
                    st.write(name)
                with row[1]:
                    st.write(f"單價：{price} 元")
                with row[2]:
                    st.write(f"數量：{q}")
                with row[3]:
                    if st.button("刪除", key=f"del_{name}"):
                        del st.session_state.cart[name]
                        try_rerun()

            st.divider()
            total = calc_total(st.session_state.cart)
            st.subheader(f"💰 總金額：{total} 元")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("🧾 結帳", use_container_width=True):
                    checkout()
            with c2:
                if st.button("🧹 清空購物車", use_container_width=True):
                    st.session_state.cart = {}
                    st.toast("已清空購物車")
                    try_rerun()

    # 收據區塊（可收合）
    st.subheader("🧾 收據")
    with st.expander("展開/收合『最近一張收據』", expanded=False):
        rec = st.session_state.last_receipt
        if not rec:
            st.caption("目前尚無最近收據。")
        else:
            st.write(f"收據編號：**{rec['id']}**")
            st.write(f"時間：**{rec['time']}**")
            for name, q in rec["items"].items():
                st.write(f"- {name} × {q}（單價 {MENU[name]['price']} 元）")
            st.write(f"**總金額：{rec['total']} 元**")

    st.caption("© Eddie demo · 若圖片未顯示，請確認 `images/` 目錄與檔名是否正確。")

