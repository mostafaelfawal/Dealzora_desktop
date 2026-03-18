from models.settings import SettingsModel
from utils.ar_support import ar

def format_currency(value):
    c = SettingsModel().get_setting("currency")
    return f"{value:,.2f} {ar(c)}"
