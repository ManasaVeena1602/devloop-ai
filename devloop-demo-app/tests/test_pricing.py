from store.pricing import calculate_order_total, apply_discount

def test_apply_discount():
    assert apply_discount(100, 10) == 90.0

def test_order_total_no_discount():
    items = [{"price": 50, "quantity": 2}]
    result = calculate_order_total(items)
    assert result == 100.0

def test_order_total_multiple_items():
    items = [
        {"price": 20, "quantity": 3},
        {"price": 15, "quantity": 1}
    ]
    result = calculate_order_total(items)
    assert result == 75.0
