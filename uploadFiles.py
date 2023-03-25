import datetime
import os
import pathlib
from queue import Queue
from tkinter.filedialog import *
import ttkbootstrap as ttk
import ttkbootstrap.dialogs
from ttkbootstrap.constants import *
from ttkbootstrap import utility
import switchWindows
from ttkbootstrap import Scrollbar
from enAndDecrypt import *


class UploadFiles(ttk.Frame):
    queue = Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=(40, 20))
        self.mainUIPage = None
        self.pack(fill=BOTH, expand=YES)
        self.create_header()

        # application variables
        _path = pathlib.Path().absolute().as_posix()
        self.path_var = ttk.StringVar(value=_path)
        self.keywords_var = ttk.StringVar(value='Enter the keywords, separated by ";"')

        # header and labelframe option container
        option_text = "Complete the form to begin your upload"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.xscroll = Scrollbar(self, orient=HORIZONTAL)
        self.yscroll = Scrollbar(self, orient=VERTICAL)

        self.create_path_row()
        self.create_keywords_row()
        self.create_backbutton_row()
        self.create_results_view()

    def create_header(self):
        labelTitle = ttk.Label(
            master=self,
            text="Files-Upload",
            bootstyle=(SUCCESS, INVERSE),
            padding=10,
        )
        labelTitle.pack(fill=X, expand=YES, pady=10)

    def create_path_row(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="Path", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row,
            text="Browse",
            command=self.on_browse,
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_keywords_row(self):
        """Add term row to labelframe"""
        keywords_row = ttk.Frame(self.option_lf)
        keywords_row.pack(fill=X, expand=YES, pady=15)
        term_lbl = ttk.Label(keywords_row, text="Keywords", width=8)
        term_lbl.pack(side=LEFT, padx=(15, 0))
        term_ent = ttk.Entry(keywords_row, textvariable=self.keywords_var)
        term_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        upload_btn = ttk.Button(
            master=keywords_row,
            text="Upload",
            command=self.on_upload,
            bootstyle=OUTLINE,
            width=8
        )
        upload_btn.pack(side=LEFT, padx=5)

    def create_backbutton_row(self):
        backbutton_row = ttk.Frame(self.option_lf)
        backbutton_row.pack(fill=X, expand=YES, pady=5)
        back_btn = ttk.Button(
            master=backbutton_row,
            text="Return",
            command=self.on_back,
            bootstyle=(WARNING, OUTLINE),
            width=8
        )
        back_btn.pack(side=BOTTOM, padx=40)
        refresh_btn = ttk.Button(
            master=backbutton_row,
            text="Refresh",
            command=self.on_refresh,
            bootstyle=(INFO, OUTLINE),
            width=8
        )
        refresh_btn.pack(side=RIGHT, padx=5)

    def create_results_view(self):
        """Add result treeview to labelframe"""
        self.resultview = ttk.Treeview(
            master=self,
            columns=[0, 1, 2, 3],
            height=10,
            show=HEADINGS,
            style='Treeview',
            xscrollcommand=self.xscroll.set,
            yscrollcommand=self.yscroll.set
        )
        self.xscroll.config(command=self.resultview.xview)
        self.yscroll.config(command=self.resultview.yview)

        self.resultview.pack(fill=BOTH, expand=YES, pady=5)
        self.resultview.bind("<Double-1>", self.download)

        # setup columns and use `scale_size` to adjust for resolution
        self.resultview.heading(0, text='ID', anchor=W)
        self.resultview.heading(1, text='FileName', anchor=W)
        self.resultview.heading(2, text='UploadTime', anchor=W)
        self.resultview.heading(3, text='Size', anchor=W)
        self.resultview.column(
            column=0,
            anchor=W,
            width=utility.scale_size(self, 190),
            stretch=False
        )
        self.resultview.column(
            column=1,
            anchor=W,
            width=utility.scale_size(self, 350),
            stretch=False
        )
        self.resultview.column(
            column=2,
            anchor=W,
            width=utility.scale_size(self, 350),
            stretch=False
        )
        self.resultview.column(
            column=3,
            anchor=W,
            width=utility.scale_size(self, 190),
            stretch=False
        )
        self.on_refresh()

    def on_upload(self):
        dealFile = EnAndDecrypt(self.path_var.get(), self.keywords_var.get())
        if dealFile.connectDB() is False:
            ttkbootstrap.dialogs.Messagebox.show_question(title="Question", message="Error, Please check the database!")
            return

        if os.path.exists(str(self.path_var.get())) is False or dealFile.judgeType() is False:
            ttkbootstrap.dialogs.Messagebox.show_question(title="Question", message="File does not exist or file type "
                                                                                    "error!")
            dealFile.closeDB()
            return

        dealFile.startEncrypt()
        dealFile.closeDB()
        ttkbootstrap.dialogs.Messagebox.show_info(title="Information", message="File upload successful!")

    def on_refresh(self):
        getclass = EnAndDecrypt("NULL", "NULL")
        getclass.connectDB()
        dataList = getclass.searchTableFirst()
        getclass.closeDB()

        x = self.resultview.get_children()
        if len(x) != 0:
            for item in x:
                self.resultview.delete(item)

        for i in range(len(dataList)):
            j = dataList[i]
            self.resultview.insert(
                parent='',
                index=END,
                values=(str(j[1]), str(j[2]), str(j[3]), str(j[4]))
            )
    def download(self, event):
        table = event.widget
        for item in table.selection():  # 取消表格选取
            table.selection_remove(item)
        self.row = table.identify_row(event.y)  # 点击的行
        self.column = table.identify_column(event.x)  # 点击的列
        col = int(str(table.identify_column(event.x)).replace('#', ''))  # 列号
        text = table.item(self.row, 'value')[col - 1]  # 单元格内容
        if col == 2:
            getclass = EnAndDecrypt("NULL", "NULL")
            if getclass.downloadFile(str(text)):
                ttkbootstrap.dialogs.Messagebox.show_info(title="Information", message="File download successful!")
            else:
                ttkbootstrap.dialogs.Messagebox.show_question(title="Question",
                                                              message="File download error!")

    def on_browse(self):
        """Callback for directory browse"""
        path = askopenfilename(title="Browse directory")
        if path:
            self.path_var.set(path)

    def on_back(self):
        # start search in another thread to prevent UI from locking
        self.pack_forget()
        switchWindows.UFToMain(self.master)

    def convert_size(self, size):
        """Convert bytes to mb or kb depending on scale"""
        kb = size // 1000
        mb = round(kb / 1000, 1)
        if kb > 1000:
            return f'{mb:,.1f} MB'
        else:
            if kb == 0:
                kb = 1
            return f'{kb:,d} KB'


if __name__ == "__main__":
    app = ttk.Window(
        title="Files-Upload",
        size=(900, 600),
        resizable=(False, False)
    )
    UploadFiles(app)
    app.mainloop()
