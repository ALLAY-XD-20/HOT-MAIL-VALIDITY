# 🎮 ALPHA DEV - Minecraft HOTMAIL Account Checker

A blazing-fast combo checker for Minecraft accounts linked to **Hotmail / Outlook / Live (Microsoft)** emails.

> ✅ **Main Platform:** Android (Termux / Pydroid3)  
> 💻 Also includes a GUI version for PC (Python + Tkinter)  
> 🎯 Checks only Microsoft-based email logins used in Minecraft

---

## 🚀 Features

- 🧪 Verifies Hotmail/Outlook/Live `email:password` combos
- ✅ Detects:
  - ✔️ Valid logins (non-2FA)
  - 🔐 2FA-protected accounts
  - ❌ Invalid or banned accounts
- 🧵 Multi-threaded for high-speed checking
- 📂 Loads `.txt` combo lists from folder
- 💾 Auto-saves results by file and category
- 🖥️ PC GUI version included
- 📱 Android is the main optimized platform

---

## 📑 Input & Output Example

### 🔹 Combo Format (Input)

Each `.txt` file should be formatted like:
@hotmail , @outlook , etc 
> 🚫 **No spaces**, no extra symbols. Only `email:password`

---

### 📂 Output Folder Structure

Results will be saved automatically like this:
results/ └── list1.txt/ ├── Valid.txt      ✅ Successful logins ├── 2FA.txt        🔐 Requires 2FA └── Bad.txt        ❌ Invalid/disabled credentials
---

## 📱 Android Setup (Main Platform)

### 📲 Requirements
- [Termux (F-Droid)](https://f-droid.org/en/packages/com.termux/) or [Pydroid3 (Play Store)](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3)
- Python 3.10+ or 3.12

---


### 🛠️ Install & Run

```bash
pkg update -y && pkg install python git -y
pip install requests colorama
git clone https://github.com/ALLAY-XD-20/HOT-MAIL-VALIDITY.git
cd HOT-MAIL-VALIDITY
python main.py
