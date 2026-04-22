# ACAT – Automated Comprehensibility Assessment Tool

Cross-platform rewrite using **CustomTkinter** instead of PyQt6.  
Works on **Windows, macOS, and Linux** without crashes.

---

## 1 · Run in development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python -m acat
```

---

## 2 · Build a standalone executable

### All platforms
```bash
pip install pyinstaller
pyinstaller build.spec
```

The output is in `dist/`:
- **Windows** → `dist/ACAT.exe`
- **macOS**   → `dist/ACAT.app`
- **Linux**   → `dist/ACAT`

> **Note:** build on the target platform — a Windows build must be run on
> Windows, a macOS build on macOS, etc.

---

## 3 · What changed

Only the `acat/ui/` layer was rewritten.  
The entire `acat/backend/` (Praat scripts, scoring formulas) is **unchanged**.

| Old (PyQt6)           | New (CustomTkinter)      |
|-----------------------|--------------------------|
| `QMainWindow`         | `ctk.CTk`                |
| `QWidget`             | `ctk.CTkFrame`           |
| `CTkToplevel`         | `ctk.CTkToplevel`        |
| `QTableWidget`        | `ctk.CTkScrollableFrame` |
| `QThreadPool`         | `threading.Thread`       |
| `pyqtSignal`          | `queue.Queue` + `after`  |
| `QComboBox`           | `ctk.CTkComboBox`        |
| `QFileDialog`         | `tkinter.filedialog`     |
| `QMessageBox`         | `tkinter.messagebox`     |

---

## 4 · Features

- Choose single or multiple audio files
- Judge individual files or all at once (background thread, non-blocking)
- View detailed score breakdown per file (Info popup)
- Score interpretation rubrics (Help window)
- Export all results to CSV
- Follows OS light / dark mode automatically
