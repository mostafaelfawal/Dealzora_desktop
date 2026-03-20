from models.settings import SettingsModel

def format_currency(value):
    c = SettingsModel().get_setting("currency")
    return f"{value:,.2f} {c}"
