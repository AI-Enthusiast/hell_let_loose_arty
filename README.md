# Hell Let Loose Artillery Calculator

A Python automation tool for the WW2 tactical shooter "Hell Let Loose" that assists with artillery calculations and firing operations.

> ⚠️ **DISCLAIMER**: This tool is for educational purposes only. Use at your own risk. Automating game inputs may violate the game's terms of service and could result in account penalties or bans. The authors are not responsible for any consequences of using this software.

## Features

- **Artillery Calculator Integration**: Scrapes data from [hell-let-loose-calculator.com](https://www.hell-let-loose-calculator.com/) to get accurate elevation and bearing values
- **Automated Gun Aiming**: Automatically adjusts gun elevation (MIL) and bearing (degrees) using OCR feedback
- **Fire Control**: Automated firing and reloading sequences with configurable shot counts
- **Area Saturation**: Fire at multiple points within a specified radius to cover an area
- **AFK Prevention**: Mouse wiggler utility to prevent being kicked for inactivity
- **Kill Switch**: Press 'F' key to instantly stop any ongoing operation

## Supported Maps

- Carentan
- Driel
- El Alamein
- Foy
- Hill 400
- Hürtgen Forest
- Kharkov
- Elsenborn Ridge
- Utah Beach
- Omaha Beach
- Purple Heart Lane
- Remagen
- Stalingrad

## Requirements

- Windows OS
- Python 3.8+
- Firefox browser (for Selenium WebDriver)
- Tesseract OCR installed (default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
  - If installed elsewhere, update the path in `arty_website.py`
- Dual monitor setup recommended (game on primary, calculator on secondary)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AI-Enthusiast/hell_let_loose_arty.git
   cd hell_let_loose_arty
   ```

2. Install Python dependencies:
   ```bash
   pip install requests selenium pynput pillow opencv-python numpy pytesseract tqdm pywin32 pyvirtualdisplay
   ```

3. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for Windows

4. Install [Firefox](https://www.mozilla.org/firefox/) and [geckodriver](https://github.com/mozilla/geckodriver/releases)

## Usage

### Main Artillery Tool

```bash
python arty_website.py
```

1. Select a map from the numbered list
2. Select an artillery gun position
3. Use the web calculator to mark targets
4. Press 'f' to fire at the target, 's' to saturate an area, or Enter to skip

### AFK Prevention

```bash
python afk.py
```

Press `Alt+Shift+W` to toggle the mouse wiggler on/off.

### Artillery Reloader

```bash
python arty_reloader.py
```

Press `Alt+Shift+R` to toggle automatic 'R' key spam for reloading.

## Controls

| Key | Action |
|-----|--------|
| F | Kill switch - stops any ongoing operation |
| W/S | Adjust elevation (up/down) |
| A/D | Adjust bearing (left/right) |
| F1 | Switch to gun position 1 |
| F2 | Switch to gun position 2 |
| Alt+Shift+W | Toggle AFK prevention |
| Alt+Shift+R | Toggle auto-reload |

## How It Works

1. **Map Selection**: User selects a map and gun position
2. **Web Scraping**: Selenium scrapes the artillery calculator website for gun data
3. **OCR Reading**: The tool reads current elevation and bearing from the game screen using Tesseract OCR
4. **Auto-Adjustment**: Keyboard inputs are simulated to adjust the gun to the target values
5. **Firing**: The tool can automatically fire and reload the artillery piece

## Project Structure

```
hell_let_loose_arty/
├── arty_website.py      # Main artillery automation tool
├── arty_reloader.py     # Auto-reload utility
├── afk.py               # AFK prevention mouse wiggler
├── test_scrape.py       # Web scraping test script
├── proto.ipynb          # Development prototype notebook
└── website_scraper.ipynb # Web scraping experiments
```

## Disclaimer

This tool is for educational purposes only. Use at your own risk. Automating game inputs may violate the game's terms of service and could result in account penalties or bans.

## License

This project is provided as-is without any warranty. Feel free to use and modify for personal use.
