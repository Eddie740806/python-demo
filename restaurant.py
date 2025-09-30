menu = {
    "牛肉麵": 120,
    "滷肉飯": 80,
    "珍珠奶茶": 60
}

print("👋 歡迎光臨 Eddie 小餐廳！")
print("今日菜單：")
for item, price in menu.items():
    print(f"- {item}: {price} 元")

orders = []
total = 0

while True:
    order = input("輸入要點的餐點（輸入 q 結束）：")
    if order == "q":
        break
    if order in menu:
        orders.append(order)
        total += menu[order]
        print(f"已加入 {order}，目前金額 {total} 元")
    else:
        print("❌ 沒有這個餐點")

print("📜 您的點餐清單：", orders)
print(f"💰 總金額：{total} 元")
