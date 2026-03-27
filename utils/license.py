import hashlib
import uuid
import winreg
import socket
from pathlib import Path

SECRET_KEY = "mostafa-hamdi-dealzora"

LICENSE_FILE = Path.home() / ".dealzora_license"
HWID_FILE = Path.home() / ".dealzora_hwid"  # ملف لحفظ HWID الثابت


def get_machine_guid():
    """الحصول على GUID ثابت للجهاز"""
    try:
        # محاولة الحصول على MachineGUID من الريجستري
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
        )
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        if guid:
            return guid
    except:
        pass

    # إذا فشل، استخدام معرف ثابت من القرص الصلب
    try:
        # الحصول على Serial Number من القرص الصلب C:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32

        # تعريف هيكل volume information
        volume_serial = ctypes.c_uint32()
        ret = kernel32.GetVolumeInformationW(
            "C:\\", None, 0, ctypes.byref(volume_serial), None, None, None, 0
        )

        if ret:
            return f"HDD-{volume_serial.value:08X}"
    except:
        pass

    # إذا فشل كل شيء، استخدام معرف من ملف ثابت
    return get_or_create_hwid()


def get_or_create_hwid():
    """إنشاء أو استرجاع HWID ثابت من ملف"""
    if HWID_FILE.exists():
        return HWID_FILE.read_text().strip()

    # إنشاء HWID جديد باستخدام معلومات متعددة
    try:
        # جمع معلومات متنوعة من الجهاز
        computer_name = socket.gethostname()
        cpu_id = get_cpu_id()
        motherboard_serial = get_motherboard_serial()

        combined = f"{computer_name}-{cpu_id}-{motherboard_serial}"
        hwid = hashlib.sha256(combined.encode()).hexdigest()[:32]

        # حفظ HWID في ملف
        HWID_FILE.write_text(hwid)
        return hwid
    except:
        # إذا فشل كل شيء، استخدم UUID عشوائي
        hwid = str(uuid.uuid4())
        HWID_FILE.write_text(hwid)
        return hwid


def get_cpu_id():
    """الحصول على معرف المعالج"""
    try:
        import subprocess

        # استخدام WMIC للحصول على معرف المعالج
        result = subprocess.run(
            ["wmic", "cpu", "get", "processorid"], capture_output=True, text=True
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            cpu_id = lines[1].strip()
            if cpu_id:
                return cpu_id
    except:
        pass
    return "UNKNOWN_CPU"


def get_motherboard_serial():
    """الحصول على الرقم التسلسلي للوحة الأم"""
    try:
        import subprocess

        # استخدام WMIC للحصول على الرقم التسلسلي للوحة الأم
        result = subprocess.run(
            ["wmic", "baseboard", "get", "serialnumber"], capture_output=True, text=True
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            serial = lines[1].strip()
            if serial and serial != "To be filled by O.E.M.":
                return serial
    except:
        pass
    return "UNKNOWN_MOTHERBOARD"


def get_machine_fingerprint():
    """الحصول على بصمة ثابتة للجهاز"""
    guid = get_machine_guid()
    if not guid:
        return None

    raw = f"{guid}-{SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_expected_license():
    """إنشاء الترخيص المتوقع بناءً على معلومات الجهاز"""
    fingerprint = get_machine_fingerprint()
    return fingerprint


def is_license_valid():
    """التحقق من صحة الترخيص"""
    if not LICENSE_FILE.exists():
        return False

    saved_license = LICENSE_FILE.read_text().strip()
    expected_license = generate_expected_license()

    return saved_license == expected_license


def save_license(license_key: str):
    """حفظ مفتاح الترخيص"""
    LICENSE_FILE.write_text(license_key)


def activate_license():
    """تفعيل الترخيص (إنشاء ملف الترخيص)"""
    expected = generate_expected_license()
    if expected:
        save_license(expected)
        return True
    return False


def is_activated():
    """التحقق مما إذا كان البرنامج مفعل بالفعل"""
    return LICENSE_FILE.exists() and is_license_valid()
