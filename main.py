import sys, os, django
sys.dont_write_bytecode = True 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings") 
django.setup()

from db import models

# TODO: check the forced files was cleaned after each bakup

import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
gdrive = GoogleDrive(gauth)

def backup(path, gid, ref, lastref, ver, forced):
    for filename in os.listdir(path):
        print(filename)
        if os.path.isdir(path+"\\"+filename):
            """
            If the filename it's a folder, we create the folder and then check if the filename exists in the previous bakup,
            if it exixst then we compare if both (The actual file and the previous) are folders, if this situation it's true
            then we use recursion using the previous folder in 'lastref', else, we pass an empty dict.
            """
            gfolder = gdrive.CreateFile({'title': filename, "parents":  [{"id": gid}], "mimeType": "application/vnd.google-apps.folder"})
            gfolder.Upload()

            ref[filename] = {"gid": gfolder["id"], "subFiles": {}}
            if filename in lastref and "subFiles" in lastref[filename]: # The folder it's in the prev bak and not present changes
                backup(path+"\\"+filename, gfolder["id"], ref[filename]["subFiles"], lastref[filename]["subFiles"], ver, forced)

            else:
                backup(path+"\\"+filename, gfolder["id"], ref[filename]["subFiles"], {}, ver, forced)

        else:
            """
            if the local filename is a file, then whe check the filename exists in the previous backup,
            if the filename exists then whe check if is a file or a folder, if it's a file whe reuse his 
            ref info, else, whe upload the file and create a new ref info.
            """

            # |-------------NOT IN FORCED---------AND------------------------IN LAST BACKUP---------------------|
            if not path+"\\"+filename in forced and filename in lastref and not "subFiles" in lastref[filename]:
                ref[filename] = lastref[filename]

            else:
                gfile = gdrive.CreateFile({"title": filename, "parents": [{"id": gid}]})
                gfile.SetContentFile(path+"\\"+filename)
                gfile.Upload()

                ref[filename] = {"gid": gfile["id"], "ver": ver}

def getref(gid, ver):
    prevFol = gdrive.ListFile({'q': f"'{gid}' in parents and trashed=false and title='{ver}'"}).GetList()
    if prevFol:
        prevFol = prevFol[0]["id"]
        lastref = gdrive.ListFile({'q': f"'{prevFol}' in parents and trashed=false and title='ref.json'"}).GetList()
        if lastref:
            lastref = lastref[0].GetContentString()
            if lastref:
                lastref = json.loads(lastref)
                return lastref
    return dict()

def getDriveFileByName(gid, name):
    files = gdrive.ListFile({'q': f"'{gid}' in parents and trashed=false and title='{name}'"}).GetList()
    return files

def getFiles(ref, todownload):
    for filename in ref:
        print(filename)
        if "subFiles" in ref[filename]: # It's a folder
            if not os.path.isdir(todownload+"\\"+filename):
                os.mkdir(todownload+"\\"+filename)
            else:
                raise Exception(f"The dir {todownload}\\{filename} already exists")
            getFiles(ref[filename]["subFiles"], todownload+"\\"+filename)
        else:
            #print(filename)
            file = gdrive.CreateFile({"id": ref[filename]["gid"]})
            file.GetContentFile(todownload+"\\"+filename)

class BackupHandler(FileSystemEventHandler):
    def __init__(self, info):
        self.info = info

        self.forced = list()
        self.obs = Observer()
        self.obs.schedule(self, path=self.info.path, recursive=True)
        self.obs.start()

    def backup(self):
        forced = self.forced.copy()
        self.forced.clear()
        print(forced)

        ref = dict()
        lastref = getref(self.info.gid, self.info.ver-1)
        # given a google drive id, the version folder is cretated
        verFol = gdrive.CreateFile({'title': str(self.info.ver), "parents":  [{"id":  self.info.gid}], "mimeType": "application/vnd.google-apps.folder"})
        verFol.Upload()

        # given the version folder id, the content folder
        contentFol = gdrive.CreateFile({'title': "content", "parents":  [{"id": verFol["id"]}], "mimeType": "application/vnd.google-apps.folder"})
        contentFol.Upload()

        backup(self.info.path, contentFol["id"], ref, lastref, self.info.ver, forced)

        # The ref json is uploaded
        refJSON = gdrive.CreateFile({'title': "ref.json", "parents":  [{"id": verFol["id"]}]})
        refJSON.SetContentString(json.dumps(ref))
        refJSON.Upload()

        self.info.ver += 1
        self.info.save()

    def download(self, path, ver):
        ref = getref(self.info.gid, ver)
        name = [f.GetContentString() for f in getDriveFileByName(self.info.gid, "name")][0]
        path += "\\"+name
        if os.path.isdir(path):
            raise Exception(f"The dir {path} already exists")

        os.mkdir(path)
        getFiles(ref, path)

    def on_modified(self, event):
        if not event.is_directory:
            if not event.src_path in self.forced:
                self.forced.append(event.src_path)

    def destroy(self):
        self.obs.stop()
        self.obs.join()
        print(self.info)

if __name__ == "__main__":
    print("The program is ready")
    # start
    h = list()
    for info in models.Backup.objects.all():
        bakhandler = BackupHandler(info)
        h.append(bakhandler)

    while True:
        try:
            data = input("")
            if data == "bak":
                for bakhandler in h:
                    print("backup started from", bakhandler.info.path, "to", bakhandler.info.gid)
                    bakhandler.backup()
                    print("backup ended from", bakhandler.info.path, "to", bakhandler.info.gid)

            if data.split(" ")[0] == "down":
                for bakhandler in h:
                    print("download started from", bakhandler.info.gid, "to", bakhandler.info.path)
                    bakhandler.download(data.split(" ")[1], data.split(" ")[2])
                    print("download ended from", bakhandler.info.gid, "to", bakhandler.info.path)

        except KeyboardInterrupt:
            break

    # stop
    for bakhandler in h:
        bakhandler.destroy()