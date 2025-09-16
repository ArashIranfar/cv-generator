# 🚀 Getting Started: AI-Powered CV Generator

Follow these instructions to set up and run the project on your local machine.

## 1. Prerequisites

*   Python 3.8+
*   An OpenAI API Key

## 2. Installation & Setup

**1. Clone the repository:**
```bash
git clone https://github.com/ArashIranfar/cv-generator.git
cd cv-generator
```

**2. Create and activate a virtual environment:**
```bash
# For macOS / Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

**3. Install dependencies:**

### For Windows Users (WeasyPrint Special Setup Required)

WeasyPrint requires additional setup on Windows due to its dependencies on GTK+ libraries (Pango, Cairo, GDK-PixBuf). Choose one of these methods:

#### Method 1: Using Anaconda (Recommended for Windows)
If you have Anaconda installed:
```bash
conda install -c conda-forge weasyprint
pip install -r requirements.txt --ignore-installed weasyprint
```

#### Method 2: Using Chocolatey
If you have Chocolatey package manager:
```bash
# Install GTK+ dependencies via Chocolatey
choco install gtk-runtime

# Then install Python dependencies
pip install -r requirements.txt
```

#### Method 3: Manual GTK+ Installation
1. Install MSYS2 from https://www.msys2.org/
2. Open MSYS2 terminal and run:
   ```bash
   pacman -S mingw-w64-x86_64-pango
   ```
3. Add MSYS2's mingw64/bin to your Windows PATH environment variable
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

**Note**: If you encounter C++ build tool errors, install "Microsoft Visual C++ Build Tools" from the Visual Studio website.

### For macOS/Linux Users
```bash
pip install -r requirements.txt
```

## 3. Configuration (Required)
[Rest of the configuration section remains the same...]
```

## Updated CUSTOMIZATION.md

Add this troubleshooting section to your `CUSTOMIZATION.md`:

```markdown
# 🎨 Customization: AI-Powered CV Generator

[Previous content remains the same...]

## Troubleshooting

### WeasyPrint Issues on Windows

If you encounter PDF generation errors on Windows, it's likely related to WeasyPrint's GTK+ dependencies:

1. **Missing DLL errors**: Ensure GTK+ libraries are properly installed and in your PATH
2. **Font rendering issues**: WeasyPrint may have trouble finding system fonts on Windows
3. **Antivirus false positives**: Some antivirus software may flag WeasyPrint - add an exception if needed

**Alternative Solutions**:
- Use WSL (Windows Subsystem for Linux) and follow Linux installation steps
- Consider using Docker to run the application in a Linux container
- Use a cloud deployment service that handles dependencies automatically

### PDF Generation Troubleshooting

If PDFs aren't generating correctly:
- Check that all required fonts are available on your system
- Verify CSS doesn't use unsupported properties
- Test with a minimal template first to isolate issues