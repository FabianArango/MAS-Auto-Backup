import psutil, threading, os, shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class BackupEvent(FileSystemEventHandler):
    def __init__(self, lcl, bak, exe, ver):
        self.lcl = lcl
        self.bak = bak
        self.exe = exe
        self.ver = ver
        self.fScan = False

        self.obs = Observer()
        self.obs.schedule(self, path=self.lcl, recursive=False)
        self.obs.start()

    def on_any_event(self, event):
        if not self.fScan:
            self.fScan = self.procExist()

    def procExist(self):
        var = False
        for proc in psutil.process_iter(['pid', 'exe']):
            if proc.info["exe"] == self.exe:
                proc = psutil.Process(proc.info["pid"])
                t = threading.Thread(target=self.onProcClose, args=(proc, ))
                t.start()
                var = True
                break
        return var

    def onProcClose(self, proc):
        proc.wait()
        t = self.procExist()
        if not t:
            self.backup()
            self.fScan = False

    def backup(self):
        """
        This maybe is a draft
        """
        """
        root {
            0: {1.txt, 2.txt},
            1: {2.txt},
            2: {3.txt},
            ref.json: {
                0: {1.txt, self}, {2.txt, self},
                1: {1.txt, 0}, {2.txt, self},
                2: {3.txt, self}
            }
        }
        """
        print("backup", self.exe)
        rootbak = self.bak+"\\"+self.lcl.split("\\")[-1]
        print(rootbak)
        if not os.path.isdir(rootbak):
            print("not folder name in")
            os.mkdir(rootbak)
        
        bakdir = rootbak+"\\"+str(self.ver)
        os.mkdir(bakdir)

        for filename in os.listdir(self.lcl):
            shutil.copyfile(self.lcl+"\\"+filename, bakdir+"\\"+filename)

        """
        for each file in lcl:
            if not file in backup or file was modified:
                the file is uploaded
        The back up data is given by the ref.json file
        """
        
        #The data base is updated and the version is incremmented by 1

    def destroy(self):
        self.obs.stop()
        self.obs.join()

if __name__ == "__main__":
    b = BackupEvent(
        r"C:\Users\Lenovo-PC\Desktop\scripts\AutoBackup\wathF",
        r"C:\Users\Lenovo-PC\Desktop\backup",
        r"C:\Program Files\Notepad++\notepad++.exe",
        1
        )
    while True:
        try:
            val = input("")
            if val == "bak":
                b.backup()
            else:
                print("Try again")
        except KeyboardInterrupt:
            break
    b.destroy()