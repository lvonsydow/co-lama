import os
import queue
import threading
import time
import rumps
import subprocess

class Colama(rumps.App):
    docker_images = {}

    def __init__(self):
        super(Colama, self).__init__("Co-lama")
        self.openPathSettings()
        os.environ['PATH'] += os.pathsep + self.getPath()
        self.icon = 'lama.png'
        self.menu = ["Title", rumps.separator, "Start Colima", "Stop Colima", rumps.separator, "Status", rumps.separator, "Images"]
        self.menu["Title"].title = "🦙 Co-lama"
        
        self.update_docker_status()
        self.timer = rumps.Timer(self.update_docker_status, 15)
        self.timer.start()
        
        self.docker_images_queue = queue.Queue()
        self.check_docker_images()
        self.check = rumps.Timer(self.check_docker_images, 10)
        self.check.start()
        self.images = rumps.Timer(self.update_docker_images_ui, 12)
        self.images.start()

    def check_docker_images(self, _=None):
        if self.is_docker_running():
            dockerPS = subprocess.check_output(["docker ps"], shell=True).decode('utf-8')
            dockerPS = dockerPS.split('\n')[1:]  # Skip the header row

            new_docker_images = {}  # Create a new dictionary to hold the current Docker images

            for row in dockerPS:
                if row:  # Skip empty rows
                    columns = row.split()
                    if len(columns) > 1:  # Make sure there is an image name
                        image_name = columns[1]  # The image name is the second column
                        container_id = columns[0]  # The container ID is the first column
                        new_docker_images[image_name] = container_id  # Save the container ID

            if new_docker_images != self.docker_images:
                self.docker_images = new_docker_images
                print("Updating queue")
                self.docker_images_queue.put(new_docker_images)


    def update_docker_images_ui(self, _=None):
        try:
            new_docker_images = self.docker_images_queue.get_nowait()
            if len(self.menu["Images"]) > 0:
                self.menu["Images"].clear()
            for image in new_docker_images.keys():
                print("Updating UI")
                self.menu["Images"].add(rumps.MenuItem(image, callback=self.userclick))
        except queue.Empty:
            pass

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
    
    def openActionWindow(self, image_name):
        container_id = self.docker_images[image_name]
        response = rumps.alert('Are you sure?', 'Want to stop ' + image_name + '?', ok='Destroy!', cancel='Meh')
        if response == 1:
            subprocess.run(["docker stop " + container_id], shell=True, check=True) 
            rumps.notification("Im getting tired", "I do everything for you 🙄", "I'm going back to bed")
            self.check_docker_images()
        elif response == 0:
            rumps.notification("Ok", "No worries", "Nothing happened")
    
    def openPathSettings(self, _=None):  
        actualPath=self.getPath()
        if not actualPath or actualPath == "":                
            window = rumps.Window('Nothing...', 'ALERTZ')
            window.title = '¡Hola!'
            window.message = 'Can you please tell me your path to all your programs? 🙏 (The path to where your package manager has all the stuff)'
            window.default_text = '/opt/homebrew/bin'

            response = window.run()
            if response.clicked:
                pathFile=open("path.txt", "w")
                pathFile.write(response.text)
                pathFile.close()
                actualPath=response.text
                rumps.notification("Thanks", "I will remember that", "You are the best")

    def getPath(self):
        path = "path.txt"
        if not os.path.exists(path):
            open(path, 'w').close()
            return ""
        else:
            with open(path, "r") as pathFile:
                actualPath = pathFile.readline()
            return actualPath
        
    def update_docker_status(self, _=None):
        if self.is_docker_running():
            self.menu["Status"].title = "🟢 Docker is up and running"
        else:
            self.menu["Status"].title = "🔴 Nope, not running"

if __name__ == "__main__":
    Colama().run()
