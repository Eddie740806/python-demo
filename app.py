import time
from pathlib import Path
from PIL import Image
import streamlit as st
import json
from collections import defaultdict

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
VERSION = "v2.5" # 更新版本號

# -------------------------
# 小工具函式 (Helper Functions)
# -------------------------
def load_menu_from_json(filepath: Path) -> dict:
    """從 JSON 檔案載入菜單資料"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            menu_data = json.load(f)
        return menu_data
    except FileNotFoundError:
        st.error(f"找不到菜單檔案：{filepath}")
        return {}
    except json.JSONDecodeError:
        st.error(f"菜單檔案格式錯誤，請檢查 JSON 語法：{filepath}")
        return {}

# -------------------------
# 菜單資料
# -------------------------
MENU_FILE = APP_DIR / "menu.json"
MENU = load_menu_from_json(MENU_FILE)


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
        if name in MENU:
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
        if img_path.is_file():
            try:
                # Use the file path string instead of opening with PIL to avoid
                # any PIL-specific behavior that might cause thumbnails/small images
                img = None
                img_src = str(img_path)
                # Read image metadata (used for fallback sizing). Print metadata to server log
                # when DEBUG_IMAGE=1, but avoid printing debug text into the UI.
                import os
                try:
                    with Image.open(img_path) as meta_img:
                        img_width = meta_img.size[0]
                        if os.environ.get("DEBUG_IMAGE") == "1":
                            info_keys = list(meta_img.info.keys())
                            msg = f"DEBUG: {img_path.name} — size={meta_img.size}, mode={meta_img.mode}, info_keys={info_keys}"
                            print(msg)
                except Exception as e:
                    img_width = None
                    if os.environ.get("DEBUG_IMAGE") == "1":
                        print(f"DEBUG: failed to read image metadata for {img_path.name}: {e}")

                # Prefer responsive API: width='stretch'. If not supported, fall back to a numeric
                # width based on the image's original width (cap at 600px), then to use_container_width.
                try:
                    st.image(img_src, width='stretch')
                except TypeError:
                    try:
                        fw = min(img_width, 600) if img_width else 600
                        st.image(img_src, width=fw)
                    except Exception:
                        try:
                            st.image(img_src, use_container_width=True)
                        except Exception:
                            st.image(img_src)
            except Exception as e:
                st.error(f"圖片載入失敗：{img_path.name}")
                st.exception(e)
        else:
            st.warning(f"找不到圖片檔案：{img_path.name}")

        # 名稱與價格
        st.markdown(f"### {name} — {item['price']} 元")
        if item.get("desc"):
            st.caption(item["desc"])

        # 加入購物車操作列
        c1, c2 = st.columns([3, 2])
        with c1:
            try:
                btn_added = st.button(f"➕ 加入購物車", width='stretch', key=f"btn_add_{name}")
            except TypeError:
                btn_added = st.button(f"➕ 加入購物車", use_container_width=True, key=f"btn_add_{name}")
            if btn_added:
                add_to_cart(name, 1)
                st.toast(f"已加入 {name} × 1")
                try_rerun()
        with c2:
            qty = st.number_input("數量", 1, 20, 1, key=f"qty_{name}", label_visibility="collapsed")
            try:
                btn_qty = st.button("加入指定數量", width='stretch', key=f"btn_add_qty_{name}")
            except TypeError:
                btn_qty = st.button("加入指定數量", use_container_width=True, key=f"btn_add_qty_{name}")
            if btn_qty:
                add_to_cart(name, int(qty))
                st.toast(f"已加入 {name} × {int(qty)}")
                try_rerun()


# -------------------------
# 主要介面 (Main Interface)
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

if not MENU:
    st.error("菜單載入失敗，請檢查 `menu.json` 檔案是否存在且格式正確。")
    st.stop()

# -------------------------
# 版面：左（菜單） / 右（購物車＋收據）
# -------------------------
left, right = st.columns([7, 5], gap="large")

# 左側：菜單卡片
with left:
    st.header("🍽️ 今日菜單")
    
    # 根據菜單中的 "category" 欄位來分組
    categorized_menu = defaultdict(list)
    for name, data in MENU.items():
        category = data.get("category", "其他") # 如果沒有分類，就放到「其他」
        categorized_menu[category].append((name, data))
        
    # 依序顯示每個分類和其中的餐點
    for category, items in categorized_menu.items():
        st.subheader(f"▎{category}")
        for name, data in items:
            render_menu_card(name, data)


# 右側：購物車與收據
with right:
    st.header("🛒 購物車")

    # 顯示購物車內容
    cart_box = st.container(border=True)
    with cart_box:
        if not st.session_state.cart:
            st.info("購物車是空的，先從左邊選餐點吧！")
        else:
            for name, q in list(st.session_state.cart.items()): # 使用 list() 避免在迭代時修改字典
                if name not in MENU:
                    # 如果菜單變動導致購物車商品不存在，則跳過
                    continue
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
                try:
                    checkout_btn = st.button("🧾 結帳", width='stretch', type="primary")
                except TypeError:
                    checkout_btn = st.button("🧾 結帳", use_container_width=True, type="primary")
                if checkout_btn:
                    checkout()
            with c2:
                try:
                    clear_btn = st.button("🧹 清空購物車", width='stretch')
                except TypeError:
                    clear_btn = st.button("🧹 清空購物車", use_container_width=True)
                if clear_btn:
                    st.session_state.cart = {}
                    st.toast("已清空購物車")
                    try_rerun()

    # 收據區塊（可收合）
    st.header("🧾 收據")
    with st.expander("展開/收合『最近一張收據』", expanded=False):
        rec = st.session_state.last_receipt
        if not rec:
            st.caption("目前尚無最近收據。")
        else:
            st.write(f"收據編號：**{rec['id']}**")
            st.write(f"時間：**{rec['time']}**")
            for name, q in rec["items"].items():
                if name in MENU:
                    st.write(f"- {name} × {q}（單價 {MENU[name]['price']} 元）")
            st.write(f"**總金額：{rec['total']} 元**")

    st.caption("© Eddie demo · 若圖片未顯示，請確認 `images/` 目錄與檔名是否正確。")