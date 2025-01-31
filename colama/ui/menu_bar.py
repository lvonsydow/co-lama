import asyncio
import sys
import os
from typing import Optional
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget
from PySide6.QtGui import QIcon, QAction, QCursor
from PySide6.QtCore import QTimer, Signal, QObject, Slot, Qt
import qasync
from ..services.docker_service import DockerService, ContainerInfo

class SignalEmitter(QObject):
    notify = Signal(str, str, str)  # title, message, info

class ColamaMenuBar(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        
        # Setup services and signals
        self.docker_service = DockerService()
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.notify.connect(self.show_notification)
        
        # Try to find the resource files in different locations
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        homebrew_prefix = os.path.dirname(os.path.dirname(sys.executable))  # /opt/homebrew/Cellar/co-lama/0.1.0
        
        # Try to find the icon file in different locations
        icon_paths = [
            os.path.join(base_dir, 'resources', 'lama.icns'),  # Development
            os.path.join(homebrew_prefix, 'resources', 'lama.icns'),  # Homebrew installation
        ]
        
        icon_path = next((path for path in icon_paths if os.path.exists(path)), None)
        if icon_path is None:
            print(f"Warning: Could not find icon file. Tried: {icon_paths}")
            return
        
        # Setup UI with proper icon path
        self.setIcon(QIcon(icon_path))
        
        # Create menu
        self.menu = QMenu()
        self.setup_menu()
        self.setContextMenu(self.menu)
        self.setVisible(True)
        
        # Handle icon clicks
        self.activated.connect(self._handle_activation)
        
        # Setup timers for updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_docker_status)
        self.status_timer.start(15000)  # 15 seconds
        
        self.containers_timer = QTimer()
        self.containers_timer.timeout.connect(self._update_containers)
        self.containers_timer.start(10000)  # 10 seconds

    def _handle_activation(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left click
            if self.menu.isVisible():
                self.menu.hide()

    def setup_menu(self):
        """Setup the system tray menu."""
        # Status
        self.status_action = QAction("Docker Status: Checking...")
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        
        self.menu.addSeparator()
        
        # Start Docker
        self.start_action = QAction("Start Docker")
        self.start_action.triggered.connect(self._start_docker_wrapper)
        self.menu.addAction(self.start_action)
        
        # Stop Docker
        self.stop_action = QAction("Stop Docker")
        self.stop_action.triggered.connect(self._stop_docker_wrapper)
        self.menu.addAction(self.stop_action)
        
        self.menu.addSeparator()
        
        # Create containers menu but don't add it yet
        self.containers_menu = QMenu("Containers")
        self.containers_menu_action = None  # Will be added/removed dynamically
        
        self.menu.addSeparator()
        
        # Quit action - make sure it's always visible
        self.quit_action = QAction("Quit Co-lama")
        self.quit_action.triggered.connect(self._quit_app)
        self.quit_action.setShortcut("Ctrl+Q")
        self.menu.addAction(self.quit_action)

    async def initial_update(self):
        """Run initial updates when the app starts."""
        await self._async_update_docker_status()
        await self._async_update_containers()

    def show_notification(self, title: str, message: str, info: str = ""):
        """Show a system notification."""
        self.showMessage(title, f"{message}\n{info}" if info else message)

    @Slot()
    def _quit_app(self):
        """Quit the application properly."""
        QApplication.quit()
        sys.exit(0)

    @Slot()
    def _update_docker_status(self):
        asyncio.create_task(self._async_update_docker_status())

    async def _async_update_docker_status(self):
        """Update the Docker status in the menu bar."""
        is_running = self.docker_service.is_docker_running()
        self.status_action.setText(" Docker is up and running" if is_running else " Not running")
        self.start_action.setEnabled(not is_running)
        self.stop_action.setEnabled(is_running)
        
        # Show/hide containers menu based on Docker status
        if is_running and not self.containers_menu_action:
            # Add containers menu before the last separator
            actions = self.menu.actions()
            before_quit = actions[-2]  # The separator before Quit
            self.containers_menu_action = self.menu.insertMenu(before_quit, self.containers_menu)
            await self._async_update_containers()
        elif not is_running and self.containers_menu_action:
            # Remove containers menu
            self.menu.removeAction(self.containers_menu_action)
            self.containers_menu_action = None

    @Slot()
    def _update_containers(self):
        asyncio.create_task(self._async_update_containers())

    async def _async_update_containers(self):
        """Update the containers submenu."""
        if not self.docker_service.is_docker_running():
            self.containers_menu.clear()
            return
            
        containers = self.docker_service.get_containers()
        
        # Store menu visibility state
        was_visible = self.menu.isVisible()
        
        # Clear existing menu
        self.containers_menu.clear()
        
        # Add cleanup option
        cleanup_action = QAction("Remove stopped containers")
        cleanup_action.triggered.connect(self._remove_stopped_containers_wrapper)
        self.containers_menu.addAction(cleanup_action)
        
        if containers:
            self.containers_menu.addSeparator()
            
            # Add container items
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_paths = [
                os.path.join(base_dir, 'resources', "green.png"),  # Development
                os.path.join(homebrew_prefix, 'resources', "green.png"),  # Homebrew installation
            ]
            green_icon_path = next((path for path in icon_paths if os.path.exists(path)), None)
            if green_icon_path is None:
                print(f"Warning: Could not find green icon file. Tried: {icon_paths}")
                return
            
            icon_paths = [
                os.path.join(base_dir, 'resources', "red.png"),  # Development
                os.path.join(homebrew_prefix, 'resources', "red.png"),  # Homebrew installation
            ]
            red_icon_path = next((path for path in icon_paths if os.path.exists(path)), None)
            if red_icon_path is None:
                print(f"Warning: Could not find red icon file. Tried: {icon_paths}")
                return
            
            for container in containers:
                icon_path = green_icon_path if container.is_running else red_icon_path
                icon = QIcon(icon_path)
                action = QAction(icon, f"{container.name} ({container.image})")
                action.container_id = container.container_id
                action.is_running = container.is_running
                action.triggered.connect(lambda checked=False, a=action: self._container_action_wrapper(a))
                self.containers_menu.addAction(action)
        
        # Restore menu visibility if it was visible
        if was_visible:
            self.menu.popup(QCursor.pos())

    @Slot()
    def _start_docker_wrapper(self):
        asyncio.create_task(self.start_docker())

    @Slot()
    def _stop_docker_wrapper(self):
        asyncio.create_task(self.stop_docker())

    @Slot()
    def _container_action_wrapper(self, action):
        asyncio.create_task(self._container_action(action))

    @Slot()
    def _remove_stopped_containers_wrapper(self):
        asyncio.create_task(self._remove_stopped_containers())

    async def _container_action(self, action):
        """Handle container start/stop actions."""
        if action.is_running:
            success = await self.docker_service.stop_container(action.container_id)
            if success:
                self.signal_emitter.notify.emit(
                    "Container stopped",
                    "Container has been stopped successfully",
                    ""
                )
        else:
            success = await self.docker_service.start_container(action.container_id)
            if success:
                self.signal_emitter.notify.emit(
                    "Container started",
                    "Container has been started successfully",
                    ""
                )
        
        await self._async_update_containers()

    async def start_docker(self):
        """Start Docker using Colima."""
        if self.docker_service.is_docker_running():
            self.signal_emitter.notify.emit(
                "Docker Status",
                "Docker is already running",
                "No action needed"
            )
            return
        
        self.status_action.setText(" Starting...")
        self.signal_emitter.notify.emit(
            "Docker Status",
            "Starting Docker",
            "Please wait..."
        )
        
        success = await self.docker_service.start_colima()
        if success:
            await self._async_update_docker_status()
            self.signal_emitter.notify.emit(
                "Docker Status",
                "Docker Started",
                "Docker is now running"
            )
        else:
            self.signal_emitter.notify.emit(
                "Error",
                "Failed to start Docker",
                "Please check the logs"
            )

    async def stop_docker(self):
        """Stop Docker using Colima."""
        if not self.docker_service.is_docker_running():
            self.signal_emitter.notify.emit(
                "Docker Status",
                "Docker is not running",
                "No action needed"
            )
            return
        
        self.status_action.setText(" Stopping...")
        success = await self.docker_service.stop_colima()
        if success:
            await self._async_update_docker_status()
            self.signal_emitter.notify.emit(
                "Docker Status",
                "Docker Stopped",
                "Docker has been stopped"
            )
        else:
            self.signal_emitter.notify.emit(
                "Error",
                "Failed to stop Docker",
                "Please check the logs"
            )

    async def _remove_stopped_containers(self):
        """Remove all stopped containers."""
        if not self.docker_service.is_docker_running():
            self.signal_emitter.notify.emit(
                "Error",
                "Docker is not running",
                "Cannot remove containers"
            )
            return
        
        success = await self.docker_service.remove_stopped_containers()
        if success:
            self.signal_emitter.notify.emit(
                "Cleanup",
                "Containers removed",
                "Stopped containers have been removed"
            )
            await self._async_update_containers()
        else:
            self.signal_emitter.notify.emit(
                "Error",
                "Failed to remove containers",
                "Please check the logs"
            )

if __name__ == "__main__":
    app = QApplication([])
    tray = ColamaMenuBar()
    asyncio.create_task(tray.initial_update())
    loop = qasync.QEventLoop(app)
    loop.run_forever()
