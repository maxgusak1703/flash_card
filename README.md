# 🧠 BrainVault: AI-Powered Flashcards

**BrainVault** is a modern desktop application for spaced repetition learning, built on the **GNOME ecosystem (GTK4 + Libadwaita)**. The core feature of the project is its deep integration with the **Google Gemini API**, allowing users to automatically generate study decks, topics, and definitions in seconds.

The app combines an elegant native interface with the power of generative AI for the most effective memorization experience.
<img width="1093" height="696" alt="image" src="https://github.com/user-attachments/assets/4257e51e-974a-4800-8b8d-6b49c64706a6" />

---

## ✨ Key Features

* **🤖 AI Flashcard Generator:** Integration with the `gemini-2.0-flash` model allows creating entire decks on demand. You select the topic, languages (Question/Answer), card count, and context (e.g., "for kids" or "technical jargon").
* **🎨 Modern Interface (Adwaita):** Adaptive design following GNOME Human Interface Guidelines (HIG). Supports light/dark themes, transition animations, and intuitive navigation.
* **📚 Structured Library:** Two-level organization system: **Folders** ➝ **Decks** ➝ **Cards**. This allows for convenient sorting of materials by subject.
* **🧠 Spaced Repetition:** Built-in learning algorithm that tracks progress. Cards you know less well appear more frequently. The system is based on interval changes and an ease factor.
* **💾 Local Storage:** All data (cards, progress, settings) is stored locally in JSON format, ensuring privacy and autonomy.

---

## 🛠 Tech Stack

* **Language:** Python 3
* **GUI Framework:** PyGObject (GTK 4.0, Libadwaita 1)
* **AI Engine:** Google Generative AI SDK (Gemini)
* **Data Storage:** JSON

---

## 🚀 Installation & Setup

### Prerequisites
You need GTK4 and Libadwaita libraries installed on your system.

**Ubuntu / Debian:**
```bash
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 gir1.2-adw-1
```
Fedora:
```bash
sudo dnf install gobject-introspection-devel cairo-gobject-devel pkg-config python3-devel gtk4 libadwaita
```
Installation Steps
```bash
git clone https://github.com/maxgusak1703/flash_card
cd brainvault
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```
📂 Project Structure
```bash
brainvault/
├── assets/
│   └── style.css          # Interface styling (CSS for GTK)
├── core/
│   ├── ai_service.py      # Google Gemini API logic
│   ├── config.py          # Configuration and path manager
│   └── database.py        # JSON database handler & SRS algorithm
├── ui/
│   ├── dialogs.py         # Modal windows (AI, input)
│   ├── pages.py           # Pages (Deck view, Study mode)
│   └── windows.py         # Main window and navigation
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```
