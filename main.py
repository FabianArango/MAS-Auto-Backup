import os, json, threading, shutil

def backup(src, dest, modified, banned, ref, prevref, ver):
    for entry in os.scandir(src):
        print(entry.name)
        if not entry.path in banned: # If the entry is not banned
            # If the entry is a folder
            if entry.isdir(): 
                ref[entry.name] = {}
                bakFolder = os.path.join(dest, entry.name)
                # The entry is in the last backup
                if entry.name in prevref and isinstance(prevref[entry.name], dict):
                    backup(entry.name, bakFolder, modified, banned, ref[entry.name], prevref[entry.name], ver)

                else:
                    backup(entry.name, bakFolder, modified, banned, ref[entry.name], {}, ver)
            
            # Else the entry is a file
            else:
                # The entry is in the previous backup and the entry wasn't modified
                if (entry.name in prevref and isinstance(prevref[entry.name], str)) and not entry.path in modified:
                    # instahead of backup the file, we use his previous version
                    ref[entry.name] = prevref[entry.name]

                else:
                    # Backup the file
                    bakFile = shutil.copyfile(entry.path, os.path.join(dest, entry.name))
                    ref[entry.name] = bakFile


#########################################
class DeviceSource(): # Extends from Source
    """
    An object that can make backups

    --Attr--
    path: str
        the root path used for make backups

    """
    def __init__(self, path):
        self.path = path

    def backup(self, repo):
        with os.scandir(self.path) as folder:
            for entry in folder:
                pass

    def __handle(src, dest):
        with os.scandir(src) as folder:
            for entry in folder:
                if not entry in self.banned:
                    if entry.isdir():
                        pass

                    else:
                        repo.upload(entry, "shutil.copy(file, dest)")


class DeviceRepository(): # Extends from Repository
    def __init__(self):
        pass

    def restore(self, version):
        pass


class BackupEvent():
    def __init__():
        pass
        for version in repo:
            for file in version:
                pass


    def backup(self):
        for src in self.__srcs:
            for repo in self.__repos:
                src.backup(repo)

class A():
    def __iter__(self):
        return Iter()

class Iter():
    def __init__(self):
        self.i = 0

    def __next__(self):
        self.i += 1
        if self.i > 10:
            raise StopIteration

        return self.i
            

#########################################

class DeviceRepository():
    def upload(file):
        with open(dets) as destFile:
            destFile.write(file.getContentString())

    def restore(self, version, where):
        for file in version:
            shutil.copy(file, where)

class GoogleDriveRepository():
    def upload(file):
        gdriveFile.setComtentString(file.getContentString())
        gdriveFile.upload()

    def restore(self, version):
        for file in version:
            gdriveFile.getContentFile(where)

class DeviceFile():
    def getContentString():
        with open(path) as file
            return file.read()

class GoogleDriveFile():
    def getContentString():
        return gdriveFile.getContentString()


if __name__ == "__main__":
    for n in A():
        print(n)
    
    print(1 in A())