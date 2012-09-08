#!/usr/bin/python
import Tkinter, tkFont, tkFileDialog, os
from MayCal import Interpreter

class MathEditor(Tkinter.Tk):
    def __init__(self, fileName = None, cwd = os.getcwd()):
        Tkinter.Tk.__init__(self)
        
        # Create some state variables
        self.saveFileName   = fileName
        self.cwd            = cwd
        
        # Build the menu bar
        menubar = Tkinter.Menu(self)
        self.config(menu=menubar)
        
        fileMenu = Tkinter.Menu(menubar, tearoff=False)
        fileMenu.add_command(label="Exit", underline=1, command=self.wrappedQuit, accelerator="Ctrl+Q")
        fileMenu.add_command(label="Open", underline=1, command=self.openFile)
        fileMenu.add_command(label="Save", underline=1, command=self.save, accelerator="Ctrl+S")
        fileMenu.add_command(label="Save As", underline=1, command=self.saveAs)
        
        editMenu = Tkinter.Menu(menubar, tearoff=False)
        editMenu.add_command(label="Run MayCal", underline=1, command=self.evaluate, accelerator="Ctrl+Y")
        editMenu.add_command(label="increase font size", underline=1,
                             command=self.increaseFont,
                             accelerator="Ctrl+=")
        editMenu.add_command(label="decrease font size", underline=1,
                             command=self.decreaseFont,
                             accelerator="Ctrl+-")
        
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)
        menubar.add_cascade(label="Edit", underline=0, menu=editMenu)
        
        # bind hotkeys
        self.bind_all("<Control-q>", self.wrappedQuit)
        self.bind_all("<Control-s>", self.save)
        self.bind_all("<Control-y>", self.evaluate)
        self.bind_all("<Control-=>", self.increaseFont)
        self.bind_all("<Control-minus>", self.decreaseFont)
        
        # Build widgets
        self.customFont = tkFont.Font(family="Courier", size=18)
        self.mathText = Tkinter.Text(font = self.customFont)
        self.mathText.pack(fill=Tkinter.BOTH, expand=1)
        
    def wrappedQuit(self, event=None):
        self.quit()
        
    def save(self, event=None):
        if self.saveFileName == None:   self.saveAs()
        else:                           self.saveGivenFileName()
        
    def saveAs(self, event=None):
        title = "Save file as..."
        self.cwd = os.path.dirname(self.saveFileName) if self.saveFileName != None else self.cwd
        
        self.saveFileName = tkFileDialog.asksaveasfilename(parent=self, initialdir=self.cwd, title=title)
        
        if self.saveFileName == '': self.saveFileName = None
        else:                       self.saveGivenFileName()
        
    def openFile(self, event=None):
        title = "Select file to open"
        self.cwd   = os.path.dirname(self.saveFileName) if self.saveFileName != None else self.cwd
        
        self.saveFileName = tkFileDialog.askopenfilename(parent=self, initialdir=self.cwd, title=title)
        
        if self.saveFileName == '': self.saveFileName = None
        else:                       self.openGivenFileName()
        
    # The following two methods assume self.saveFileName is a valid filename
    def saveGivenFileName(self):
        self.saveFileName = os.path.realpath(self.saveFileName)
        self.title(self.saveFileName)
        
        self.cwd = self.saveFileName
        f = open(self.saveFileName, 'w')
        f.write(self.mathText.get("1.0", Tkinter.END))
        f.close()
        
    def openGivenFileName(self):
        self.saveFileName = os.path.realpath(self.saveFileName)
        self.title(self.saveFileName)
    
        self.cwd = self.saveFileName
        
        f = open(self.saveFileName, 'r')
        self.mathText.delete("1.0", Tkinter.END)
        self.mathText.insert(Tkinter.END, f.read())
        f.close()
        
    def increaseFont(self, event=None, amount=2):
        self.customFont.configure(size= self.customFont['size'] + amount)
        
    def decreaseFont(self, event=None, amount=2):
        self.customFont.configure(size= self.customFont['size'] - amount)
        
    def evaluate(self, event=None):
        interp = Interpreter()
        text = self.mathText.get("1.0", Tkinter.END)
        
        # text turns out to be a unicode object and so behaves weirdly ...
        text = text.encode('ascii', 'ignore')
        
        text = text.splitlines()
        newText = []
        for line in text:
            newText.append(line)
            if line.startswith(';'):
                result = interp(line[1:])
                if result != None:
                    newText.append(str(result))
        self.mathText.delete("1.0",Tkinter.END)
        self.mathText.insert(Tkinter.END, '\n'.join(newText))
        
        
        
if __name__ == '__main__':
    import sys
    app = None
    if len(sys.argv) == 2:
        app = MathEditor(fileName = sys.argv[1])
        app.openGivenFileName()
    else:
        app = MathEditor()
        app.title("MayCalEditor")
    
    app.mainloop()