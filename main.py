import os, time, json
from commn import SocketServer, SocketConsumer, emmAbort
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class BackgroundApp():
    def __init__(self):
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.gdrive = GoogleDrive(gauth)

        self.server = SocketServer(HOST="127.0.0.1", PORT=3452)
        self.masConsumer = SocketConsumer(self.server, DIR="MAS")
        self.masConsumer.connect = lambda conn: print("MAS connected successfully")
        self.masConsumer.disconnect = lambda conn: self.backup(
            r"C:\Users\Lenovo-PC\Desktop\scripts\deactivableGUI\backUpFolder", 
            "1wX9N7pQ6ZlI5G4gUeTCLltdB0seu5giO",
            forced=("alwaysRe.txt", "alwaysRe2.txt")
        )

        self.guiConsumer = SocketConsumer(self.server, DIR="GUI/upload")
        self.guiConsumer.connect = lambda conn: print("GUI connected successfully")
        self.guiConsumer.disconnect = lambda conn: print("GUI disconnected successfully")

    def backup(self, path, dId, forced=None, banned=None):
        tic = time.process_time()
        
        if forced == None:
            forced = tuple()
        
        if banned == None:
            banned = tuple()

        localFiles = os.listdir(path)
        driveFiles = self.gdrive.ListFile({'q': f"'{dId}' in parents and trashed=false"}).GetList()
        driveList = [f["title"] for f in driveFiles]

        print("-"*60)
        print("Local Files:   ", localFiles)
        print("Drive Files:   ", driveList)
        print("Forced Files:  ", forced)
        print("Banned Files:  ", banned)

        self.guiConsumer.send(json.dumps({"command": "start", "value": 10}))

        upFiles = list()
        for file in localFiles:
            if not file in banned and (not file in driveList or file in forced):
                df = self.gdrive.CreateFile({"title": file, "parents": [{"id": dId}]})
                df.SetContentFile(path+"\\"+file)
                df.Upload()
                upFiles.append(file)
                self.sendtoGui(file, "Uploading Files")
        print("Uploaded Files:", upFiles)

        self.guiConsumer.send(json.dumps({"command": "start", "value": 10}))
        trFiles = list()
        for file in driveFiles: 
            if not file["title"] in localFiles:
                # Only delete gdrive the files that are not in local
                file.Trash()
                trFiles.append(file["title"])
                self.sendtoGui(file["title"], "Trashing Files")

        # The list needs to be created again to have all the uploaded files
        driveFiles = self.gdrive.ListFile({'q': f"'{dId}' in parents and trashed=false"}).GetList() 
        driveFiles = sorted(driveFiles, key = lambda e: (e["title"], e["createdDate"]))
        driveList = [f["title"] for f in driveFiles]
        print("Drive Files:   ", driveList)

        self.guiConsumer.send(json.dumps({"command": "start", "value": 10}))
        i = 1
        while i < len(driveFiles):
            file = driveFiles[i]
            lastFile = driveFiles[i-1]
            if file["title"] == lastFile["title"]:
                # Delete the older duplicates
                lastFile.Trash()
                trFiles.append(lastFile["title"])
                self.sendtoGui(lastFile["title"], "Trashing duplicates")
            i += 1
        print("Thrased Files: ", trFiles)

        toc = time.process_time()
        self.guiConsumer.send(json.dumps({"command": "end", "value": None}))
        print("Completed in:  ", toc-tic)

    def sendtoGui(self, file, process):
        self.guiConsumer.send(json.dumps({    
            "command": "file",
            "value": {
                "filename": file,
                "process": process
            }
        }))

def main():
    emmAbort()
    bgApp = BackgroundApp()

if __name__ == "__main__":
    main()