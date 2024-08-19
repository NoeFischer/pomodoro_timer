# Pomodoro Timer for macOS

A simple and customizable Pomodoro Timer application for macOS, built using Python and rumps.

## Features

- Pomodoro timer with customizable work, short break, and long break durations
- Menubar app for easy access and minimal distraction
- Notifications for completed Pomodoros and breaks
- Customizable settings for work duration, break duration, long break duration, and number of Pomodoros until a long break
- Sound alert when timer ends

## Installation

1. Built with Python 3.12.4.
2. Clone this repository or download the source code.
3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

   ```
   python main.py
   ```

2. The Pomodoro Timer icon will appear in your menubar.
3. Click on the icon to access the menu and start your Pomodoro sessions.

## Customization

You can customize the Pomodoro Timer settings through the "Settings" menu:

- Work Duration
- Break Duration
- Long Break Duration
- Number of Pomodoros until Long Break

## Building a Standalone Application

To create a standalone application that can be run without Python:

1. Install PyInstaller:

   ```
   pip install pyinstaller
   ```

2. Build the application:

   ```
   pyinstaller --onefile --windowed --add-data "pomodoro.icns:." --add-data "pomodoro_settings.json:." --icon=pomodoro.icns main.py
   ```

3. The standalone application will be created in the `dist` folder.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

