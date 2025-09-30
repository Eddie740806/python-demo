# app.py
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image

# ================= 基本設定 =================
st.set_page_config(
    page_title="Eddie 小餐廳點餐系統",
    page_icon="🍜",
    layout="wide",
)

APP_DIR = Path(__file__).parent
IMG_DIR = APP_DIR / "images"

VERSION = "v3-uber-eats"

# ================= 資料 =================
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
        "desc": "黑糖蜜滑的款 Q 珍珠！",
    },
}

# ================= 狀態初始化 =================
if "cart" not in st.session_state:
    st.session_state.cart = {}  # {item_name: qty}

if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None  # 最近一次收據

if "history" not in st.session_state:
    st.session_state.history = []  # 收據歷史（最新在最上面）


def force_rerun():
    """安全重跑（Streamlit 新舊版兼容）"""
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()  # type: ignore[attr-defined]
        except Exception:
            pass


# ================= 工具函式 =================
def add_to_cart(item: str, qty: int = 1):
    if qty <= 0:
        return
    st.session_state.cart[item] = st.session_state.cart.get(item, 0) + qty


def set_qty(item: str, qty: int):
    if qty <= 0:
        st.session_state.cart.pop(item, None)
    else:
        st.session_state.cart[item] = qty


def checkout():
    # 計算總金額
    total = 0
    for name, q in st.session_state.cart.items():
        total += MENU[name]["price"] * q

    if total == 0:
        st.info("購物車是空的，先加點什麼吧！")
        return

    # 建立收據
    ts = datetime.now()
    receipt = {
        "id": ts.strftime("%Y%m%d%H%M%S"),
        "time": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "items": {k: v for k, v in st.session_state.cart.items()},
        "total": total,
    }

    # 存到狀態
    st.session_state.last_receipt = receipt
    st.session_state.history.insert(0, receipt)  # 新的放最前面
    st.session_state.cart = {}  # 清空購物車

    st.success("✅ 結帳完成！收據已產生")
    time.sleep(0.6)
    force_rerun()


# ================= 介面樣式（讓卡片更好看） =================
st.markdown(
    """
    <style>
    .menu-card img {
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }
    .menu-title {
        font-weight: 700;
        font-size: 20px;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .menu-desc {
        color: #6b7280;
        margin-bottom: 12px;
    }
    .price-badge {
        display:inline-block;
        background:#111827;
        color:#fff;
        font-size:12px;
        padding:4px 8px;
        border-radius:10px;
        margin-left:6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 頂部版本提示（方便你辨識是否為最新）
st.caption(f"🚀 目前執行版本：**{VERSION}**")


# ================= 左圖右文的餐點卡片 =================
def render_menu_card(name: str, item: dict):
    img_path = IMG_DIR / item["img"]

    with st.container(border=True):
        left, right = st.columns([2.2, 3.2], vertical_alignment="center")
        with left:
            # 固定寬度 280、保比例，讓視覺乾淨（像 UberEats）
            st.image(str(img_path), width=280, output_format="JPEG", caption=None)

        with right:
            st.markdown(
                f"""
                <div class="menu-title">{name}<span class="price-badge">{item['price']} 元</span></div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f"<div class='menu-desc'>{item['desc']}</div>", unsafe_allow_html=True)

            c1, c2 = st.columns([3, 2], vertical_alignment="center")
            with c1:
                if st.button(f"➕ 加入購物車（{name}）", key=f"btn_add_{name}", use_container_width=True):
                    add_to_cart(name, 1)
                    st.toast(f"已加入 {name} × 1")
                    force_rerun()
            with c2:
                qty = st.number_input(
                    "數量", min_value=1, max_value=20, value=1, step=1,
                    key=f"qty_{name}", label_visibility="collapsed"
                )
                if st.button("加入指定數量", key=f"btn_addN_{name}", use_container_width=True):
                    add_to_cart(name, int(qty))
                    st.toast(f"已加入 {name} × {qty}")
                    force_rerun()


# ================= 版面：左（菜單） / 右（購物車 + 收據） =================
col_menu, col_cart = st.columns([7, 5])

with col_menu:
    st.subheader("🍽️ 今日菜單")
    # 清單式呈現
    for dish_name, info in MENU.items():
        render_menu_card(dish_name, info)
        st.divider()

with col_cart:
    st.subheader("🛒 購物車")
    with st.container(border=True):
        if not st.session_state.cart:
            st.info("購物車是空的，先從左邊選餐點吧！")
        else:
            # 列出購物車
            total = 0
            for name, q in list(st.session_state.cart.items()):
                price = MENU[name]["price"]
                line = price * q
                total += line

                r1, r2, r3, r4 = st.columns([4, 3, 3, 1])
                with r1:
                    st.write(f"**{name}**")
                with r2:
                    # 數量調整
                    new_q = st.number_input(
                        "qty",
                        1,
                        50,
                        q,
                        key=f"cart_qty_{name}",
                        label_visibility="collapsed",
                    )
                    if new_q != q:
                        set_qty(name, int(new_q))
                        force_rerun()
                with r3:
                    st.write(f"NT$ {line}")
                with r4:
                    if st.button("✖", key=f"del_{name}"):
                        set_qty(name, 0)
                        force_rerun()

            st.markdown("---")
            c1, c2 = st.columns([1, 1])
            with c1:
                st.subheader(f"🧾 總金額：NT$ {total}")
            with c2:
                c21, c22 = st.columns([1, 1])
                with c21:
                    if st.button("🧹 清空購物車", use_container_width=True):
                        st.session_state.cart = {}
                        force_rerun()
                with c22:
                    if st.button("💳 結帳", type="primary", use_container_width=True):
                        checkout()

    # 收據區塊
    st.subheader("📥 收據")
    with st.expander("🧾 展開/收合『最近一張收據』", expanded=False):
        rec = st.session_state.last_receipt
        if not rec:
            st.caption("（目前尚無最近收據）")
        else:
            st.write(f"收據編號：**{rec['id']}**")
            st.write(f"時間：**{rec['time']}**")
            for n, q in rec["items"].items():
                st.write(f"- {n} × {q}（單價 NT$ {MENU[n]['price']}）")
            st.write(f"**總金額：NT$ {rec['total']}**")

    with st.expander("📚 收據歷史", expanded=False):
        if not st.session_state.history:
            st.caption("（目前尚無歷史收據）")
        else:
            for i, rec in enumerate(st.session_state.history, start=1):
                st.markdown(
                    f"**#{i}**｜收據編號：`{rec['id']}`｜時間：{rec['time']}｜總金額：**NT$ {rec['total']}**"
                )


