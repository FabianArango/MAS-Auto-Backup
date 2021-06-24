import tkinter as tk
from tkinter import ttk
import commn, json 

"""
server to client
GET --> moving data
CHNG --> for changes
"""

class UI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection = commn.SocketClient(HOST="127.0.0.1", PORT=3452, DIR="GUI/upload") #ConnectionRefusedError
        self.connection.receive = lambda data: self.changeStates(data)

        #self.chngConn = commn.SocketClient(HOST="127.0.0.1", PORT=3452, DIR="GUI/CHNG")
        #self.chngConn.receive = lambda data: self.changeStates(data)

        self.title("Draft App")
        self.geometry("{}x{}".format(90*5+16, 200))
        self.resizable(False, False)
        self.update()

        self.progressbar = ttk.Progressbar(self, maximum=10)
        self.progressbar.place(x=30, y=60, width=200)
        self.filename = tk.Label()
        self.filename.pack()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def changeStates(self, data):
        #if not self.progressbar.winfo_ismapped()
        print(data)
        """
        {
            "command": start/end/file
            "value": value
        }
        """
        data = json.loads(data)
        command = data["command"]
        value = data["value"]

        if command == "start":
            self.progressbar["value"] = 0
            self.progressbar["maximum"] = value

        elif command == "end":
            self.filename.config(text="Process completed successfully")

        elif command == "file":
            process = value["process"]
            filename = value["filename"]
            self.filename.config(text=process+": "+filename)
            self.progressbar["value"] += 1

    def on_closing(self):
        self.connection.close()
        self.destroy()

if __name__ == "__main__":
    ui = UI()
    ui.mainloop()