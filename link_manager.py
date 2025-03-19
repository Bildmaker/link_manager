"""
Link Manager

Author: Sebastian
Date: 2025-03-18

Description:
    Link Manager is a tool that imports and manages links from .url files stored in a folder.
    It extracts URLs from .url files, sorts them, and allows the user to open them directly from the interface.

Usage:
    1. Select a folder with .url files using the 'Import Links' button.
    2. The extracted links will be displayed in a list.
    3. Double-click on a link to open it in the default browser.
    4. Use the search bar to filter the links.
    5. Use the 'Open All Links' button to open all displayed links.

Features:
    - Loads links from .url files
    - Removes duplicates and sorts links alphabetically
    - Displays error messages for invalid files
    - Automatically imports links on startup if folder is configured
    - Configurations are saved in config.json
"""

import sys
import os
import json
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QListWidget,
    QLineEdit, QFileDialog, QWidget, QHBoxLayout, QLabel, QMessageBox
)

CONFIG_FILE = "config.json"

class LinkOpenerApp(QMainWindow):
    """
    Main application window for Link Manager.

    This class creates a PyQt5-based GUI for loading, displaying,
    and opening links from .url files stored in a folder.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Link Manager (Dual Mode)")
        self.setGeometry(100, 100, 1400, 1600)

        self.initUI()

        # Separate link lists
        self.links1 = []
        self.links2 = []
        self.folder1 = ""
        self.folder2 = ""

        # Load saved configuration
        self.load_config()

    def initUI(self):
        """Initialize the main user interface."""
        main_layout = QHBoxLayout()

        # Link list 1
        self.layout1 = self.create_link_panel("Linklist 1")
        main_layout.addLayout(self.layout1)

        # Link list 2
        self.layout2 = self.create_link_panel("Linklist 2")
        main_layout.addLayout(self.layout2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_link_panel(self, title):
        """Create a panel for displaying links and controls."""
        layout = QVBoxLayout()

        # Title
        label = QLabel(title)
        label.setStyleSheet("font-size: 28px; font-weight: bold; padding-bottom: 10px;")
        layout.addWidget(label)

        # Import Button
        import_button = QPushButton("Import Links")
        import_button.setStyleSheet("font-size: 24px; padding: 12px;")
        import_button.clicked.connect(lambda: self.import_links(layout, label))
        layout.addWidget(import_button)

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search links...")
        search_bar.setStyleSheet("font-size: 22px; padding: 10px;")
        layout.addWidget(search_bar)

        # Link list
        link_list = QListWidget()
        link_list.setStyleSheet("font-size: 22px; padding: 8px;")
        link_list.itemDoubleClicked.connect(lambda item: self.open_link(item.text()))
        layout.addWidget(link_list)

        # Open all links button
        open_all_button = QPushButton("Open All Links")
        open_all_button.setStyleSheet("font-size: 24px; padding: 12px;")
        open_all_button.clicked.connect(lambda: self.open_all_links(link_list))
        layout.addWidget(open_all_button)

        # Connect search bar to filtering function
        search_bar.textChanged.connect(lambda text: self.filter_links(link_list, text))

        # Store layout elements
        layout.link_list = link_list
        layout.import_button = import_button
        layout.search_bar = search_bar
        layout.open_all_button = open_all_button
        layout.label = label

        return layout

    def import_links(self, layout, label):
        """Import links from .url files in the selected folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            links = []
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path) and file.lower().endswith('.url'):
                    link = self.extract_url_from_shortcut(file_path)
                    if link:
                        links.append(link)

            # Remove duplicates and sort alphabetically
            links = sorted(set(links))

            if layout == self.layout1:
                self.links1 = links
                self.folder1 = folder
            else:
                self.links2 = links
                self.folder2 = folder

            self.update_link_list(layout)
            label.setText(f"Folder: {os.path.basename(folder)}")

    def extract_url_from_shortcut(self, file_path):
        """Extract URL from a .url file."""
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if line.startswith('URL='):
                        return line.strip().split('=')[1]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{file_path}\n\nError: {e}")
        return None

    def update_link_list(self, layout):
        """Update the list display with imported links."""
        layout.link_list.clear()
        links = self.links1 if layout == self.layout1 else self.links2
        for link in links:
            layout.link_list.addItem(link)

    def filter_links(self, link_list, search_text):
        """Filter links based on the search text."""
        search_text = search_text.lower()
        if link_list == self.layout1.link_list:
            links = self.links1
        else:
            links = self.links2

        link_list.clear()
        filtered_links = [link for link in links if search_text in link.lower()]
        link_list.addItems(filtered_links)

    def open_link(self, link):
        """Open a single link in the default web browser."""
        webbrowser.open(link)

    def open_all_links(self, link_list):
        """Open all links in the list."""
        if link_list == self.layout1.link_list:
            links = self.links1
        else:
            links = self.links2

        for link in links:
            webbrowser.open(link)

    def load_config(self):
        """Load configuration from file."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
                self.links1 = config.get('links1', [])
                self.links2 = config.get('links2', [])
                self.folder1 = config.get('folder1', "")
                self.folder2 = config.get('folder2', "")

    def save_config(self):
        """Save current configuration to file."""
        config = {
            'links1': self.links1,
            'links2': self.links2,
            'folder1': self.folder1,
            'folder2': self.folder2
        }
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)

    def closeEvent(self, event):
        """Save configuration on close."""
        self.save_config()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LinkOpenerApp()
    window.show()
    sys.exit(app.exec_())
