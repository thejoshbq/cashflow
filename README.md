# Cashflow Desktop Application

A PySide6-based desktop application for cash flow management.

## Installation

To install the application and add it to your Ubuntu applications menu:

```bash
./install.sh
```

This will:
- Set up the Python virtual environment (if needed)
- Install all required dependencies
- Create a desktop launcher in your applications menu

## Running the Application

After installation, you can launch the application in three ways:

1. **From Applications Menu**: Search for "Cashflow" in your Ubuntu applications menu
2. **From Terminal**: Run `./main.py` from the project directory
3. **With Virtual Environment**: `.venv/bin/python main.py`

## Uninstallation

To remove the desktop launcher from your applications menu:

```bash
./uninstall.sh
```

Note: This only removes the launcher. To completely remove the application, delete the project directory.

## Dependencies

- PySide6 6.10.1
- plotly 6.5.1
- narwhals 2.15.0

## Adding a Custom Icon

To customize the application icon:

1. Add an `icon.png` file to the project root directory
2. Run `./install.sh` again to update the desktop launcher

The icon should be a PNG image, ideally 256x256 pixels or larger for best display quality.

## Development

To run the application in development mode:

```bash
source .venv/bin/activate
python main.py
```

## Project Structure

```
cashflow/
├── cashflow/           # Main application package
│   ├── __init__.py
│   ├── __main__.py     # Entry point for installed package
│   ├── app.py          # Main application logic
│   ├── node.py
│   ├── node_dialogue.py
│   └── asset_dialogue.py
├── main.py             # Direct execution entry point
├── requirements.txt    # Python dependencies
├── setup.py           # Package installation configuration
├── cashflow.desktop   # Ubuntu desktop launcher configuration
├── install.sh         # Installation script
└── uninstall.sh       # Uninstallation script
```
