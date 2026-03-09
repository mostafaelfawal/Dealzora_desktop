import hashlib
import customtkinter as ctk

# نفس السر اللي في برنامج العميل
SECRET_KEY = "mostafa-hamdi-dealzora"

def generate_license(machine_id: str) -> str:
    raw = f"{machine_id}-{SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()

def on_generate():
    machine_id = entry_machine.get().strip()
    if not machine_id:
        result_label.configure(text="دخل كود الجهاز الأول", text_color="red")
        return

    license_key = generate_license(machine_id)
    result_label.configure(
        text=f"كود التفعيل:\n{license_key}",
        text_color="green"
    )

    app.clipboard_clear()
    app.clipboard_append(license_key)


# ---------- UI ----------
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("License Generator - Dealzora")
app.geometry("500x300")

ctk.CTkLabel(
    app,
    text="ادخل كود الجهاز",
    font=("Cairo", 16)
).pack(pady=15)

entry_machine = ctk.CTkEntry(app, width=400)
entry_machine.pack(pady=10)

ctk.CTkButton(
    app,
    text="توليد كود التفعيل",
    command=on_generate,
    font=("Cairo", 16)
).pack(pady=15)

result_label = ctk.CTkLabel(app, text="", wraplength=450, font=("Cairo", 18))
result_label.pack(pady=10)

ctk.CTkLabel(
    app,
    text="(تم نسخ كود التفعيل تلقائيًا)",
    font=("Cairo", 12),
    text_color="gray"
).pack(pady=5)

app.mainloop()
