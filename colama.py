import os
import rumps
import subprocess


class Colama(rumps.App):
    docker_images = {} 
    def __init__(self):
        super(Colama, self).__init__("Co-lama")

        os.environ['PATH'] += os.pathsep + '/opt/homebrew/bin'
        self.icon = 'lama.png'
        self.menu = ["Title", rumps.separator, "Start Colima", "Stop Colima", rumps.separator, "Status", rumps.separator, "Images"]
        self.menu["Title"].title = "🦙 Co-lama"
        self.update_docker_status()
        self.timer = rumps.Timer(self.update_docker_status, 15)
        self.timer.start()

    def userclick(self, menuitem):
        self.openActionWindow(menuitem.title)

    def is_docker_running(self):
        try:
            subprocess.check_output(["docker info"], shell=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @rumps.clicked("Start Colima")
    def start_colima(self, _):
        if self.is_docker_running():
            rumps.notification("ZzZzZ", "Docker is already running pal", "You are already there!")
            return
        self.menu["Status"].title = "🟡 Starting..."
        rumps.notification("Yeah Boi", "We're trying to start Docker", "Hang in there buddy, no stress")
        subprocess.run(["colima start"], shell=True, check=True)
        self.menu["Status"].title = "🟢 Docker is up and running"
        rumps.notification("🦙🦙🦙🦙🦙", "Dude..", "We did it")

    @rumps.clicked("Stop Colima")
    def stop_colima(self, _):
        if not self.is_docker_running():
            rumps.notification("Buuuuuuh", "Docker is not running", "Can´t stop what is not running dummy")
            return
        self.menu["Status"].title = "🟡 Stopping..."
        subprocess.run(["colima stop"], shell=True, check=True)
        self.menu["Status"].title = "🔴 Nope, not running"
        rumps.notification("Finally", "Going back to bed", "Maybe something to eat.. cake?")

    def update_docker_status(self, _=None):
        if self.is_docker_running():
            self.menu["Status"].title = "🟢 Docker is up and running"
        else:
            self.menu["Status"].title = "🔴 Nope, not running"

if __name__ == "__main__":
    Colama().run()
