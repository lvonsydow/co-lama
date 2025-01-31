from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import asyncio
import docker
import subprocess
from rich.console import Console

console = Console()

@dataclass
class ContainerInfo:
    container_id: str
    name: str
    image: str
    status: str
    is_running: bool

class DockerService:
    def __init__(self):
        self.client: Optional[docker.DockerClient] = None
        self._ensure_path()
    
    def _ensure_path(self) -> None:
        """Ensure the Docker path is properly set up."""
        try:
            with open("path.txt", "r") as f:
                path = f.readline().strip()
                if path:
                    import os
                    os.environ['PATH'] += os.pathsep + path
        except FileNotFoundError:
            pass

    async def start_colima(self) -> bool:
        """Start Colima and Docker daemon."""
        try:
            process = await asyncio.create_subprocess_shell(
                "colima start",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            if process.returncode == 0:
                self.client = docker.from_env()
                return True
            return False
        except Exception as e:
            console.print(f"[red]Error starting Colima: {e}[/red]")
            return False

    async def stop_colima(self) -> bool:
        """Stop Colima and Docker daemon."""
        try:
            process = await asyncio.create_subprocess_shell(
                "colima stop",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            if self.client:
                self.client.close()
                self.client = None
            return process.returncode == 0
        except Exception as e:
            console.print(f"[red]Error stopping Colima: {e}[/red]")
            return False

    def is_docker_running(self) -> bool:
        """Check if Docker daemon is running."""
        try:
            if not self.client:
                self.client = docker.from_env()
            self.client.ping()
            return True
        except:
            self.client = None
            return False

    def get_containers(self) -> List[ContainerInfo]:
        """Get all containers with their status."""
        if not self.is_docker_running():
            return []
        
        containers = []
        try:
            for container in self.client.containers.list(all=True):
                containers.append(ContainerInfo(
                    container_id=container.id[:12],
                    name=container.name,
                    image=container.image.tags[0] if container.image.tags else "none",
                    status=container.status,
                    is_running=container.status == "running"
                ))
        except Exception as e:
            console.print(f"[red]Error getting containers: {e}[/red]")
        
        return containers

    async def start_container(self, container_id: str) -> bool:
        """Start a specific container."""
        if not self.is_docker_running():
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.start()
            return True
        except Exception as e:
            console.print(f"[red]Error starting container: {e}[/red]")
            return False

    async def stop_container(self, container_id: str) -> bool:
        """Stop a specific container."""
        if not self.is_docker_running():
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return True
        except Exception as e:
            console.print(f"[red]Error stopping container: {e}[/red]")
            return False

    async def remove_stopped_containers(self) -> bool:
        """Remove all stopped containers."""
        if not self.is_docker_running():
            return False
        
        try:
            self.client.containers.prune()
            return True
        except Exception as e:
            console.print(f"[red]Error removing containers: {e}[/red]")
            return False
