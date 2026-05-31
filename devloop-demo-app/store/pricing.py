def apply_discount(price, discount_percent):
    return price - (price * discount_percent / 100)

def calculate_order_total(items):
    subtotal = 0
    for item in items:
        subtotal += item["price"] * item["quantity"]

    discount = get_seasonal_discount()
    total = apply_discount(subtotal, discount)
    return round(total, 2)

def get_seasonal_discount():
    # BUG: returns None when no active season — crashes calculate_order_total
    active_seasons = []
    if active_seasons:
        return active_seasons[0]["discount"]
    return None  # <-- this None flows into apply_discount and crashes
