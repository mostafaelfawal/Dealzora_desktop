import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Cairo"

def ar(text):
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    return bidi_text