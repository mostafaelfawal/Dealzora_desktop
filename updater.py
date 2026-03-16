import os
import time

time.sleep(2)

if os.path.exists("Dealzora.exe"):
    os.remove("Dealzora.exe")

os.rename("update.exe", "Dealzora.exe")

os.startfile("Dealzora.exe")