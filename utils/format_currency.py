from models.settings import SettingsModel

def format_currency(value):
    c = SettingsModel().get_setting("currency")
    places = SettingsModel().get_setting("decimal_places") or 2
    return f"{value:,.{places}f} {c}"
