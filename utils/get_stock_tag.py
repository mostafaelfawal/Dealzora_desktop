def get_stock_tag(qty, low):
    if qty == 0:
        return "danger"
    if qty <= low:
        return "warning"
    return "success"
