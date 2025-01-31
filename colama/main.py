import sys
import asyncio
from PySide6.QtWidgets import QApplication
import qasync
from colama.ui.menu_bar import ColamaMenuBar

def main():
    """Main entry point for the Colama application."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Create event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Create menu bar
    tray = ColamaMenuBar()
    
    # Run initial updates
    loop.create_task(tray.initial_update())
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
