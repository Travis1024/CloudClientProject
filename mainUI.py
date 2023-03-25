from ttkbootstrap import Scrollbar
import ttkbootstrap
import ttkbootstrap as ttk
from ttkbootstrap import utility
from ttkbootstrap.constants import *
import switchWindows
from enAndDecrypt import EnAndDecrypt


class MainUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=(40, 20))

        self.searchFilesPage = None
        self.pack(fill=BOTH, expand=YES)

        # header and labelframe option container
        option_text = "Select the button you want to click"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.xscroll = Scrollbar(self, orient=HORIZONTAL)
        self.yscroll = Scrollbar(self, orient=VERTICAL)

        self.create_function_row()
        self.create_refresh_row()
        self.create_results_view()


    def create_function_row(self):
        function_row = ttk.Frame(self.option_lf)
        function_row.pack(fill=X, expand=YES, pady=30)

        upload_btn = ttk.Button(
            master=function_row,
            text="FilesUpload",
            command=self.on_upload,
            bootstyle=OUTLINE,
            width=12
        )
        upload_btn.pack(side=LEFT, padx=68)

        search_btn = ttk.Button(
            master=function_row,
            text="FilesSearch",
            command=self.on_search,
            bootstyle=OUTLINE,
            width=12,
        )
        search_btn.pack(side=LEFT, padx=60)

        quit_btn = ttk.Button(
            master=function_row,
            text="Quit",
            command=self.on_quit,
            bootstyle=(WARNING, OUTLINE),
            width=12
        )
        quit_btn.pack(side=LEFT, padx=80)


    def create_refresh_row(self):
        refresh_row = ttk.Frame(self.option_lf)
        refresh_row.pack(fill=X, expand=YES)
        refresh_btn = ttk.Button(
            master=refresh_row,
            text="Refresh",
            command=self.on_refresh,
            bootstyle=(INFO, OUTLINE),
            width=12
        )
        refresh_btn.pack(expand=YES, side=TOP, padx=10)

    def create_results_view(self):
        """Add result treeview to labelframe"""
        self.resultview = ttk.Treeview(
            master=self,
            columns=[0, 1, 2, 3],
            height=19,
            show=HEADINGS,
            style='Treeview',
            xscrollcommand=self.xscroll.set,
            yscrollcommand=self.yscroll.set
        )
        self.xscroll.config(command=self.resultview.xview)
        self.yscroll.config(command=self.resultview.yview)

        self.resultview.pack(expand=YES, pady=5, side=TOP)
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


    def on_quit(self):
        """Quit the application."""
        self.quit()

    def on_upload(self):
        self.pack_forget()
        switchWindows.MainToUF(self.master)

    def on_search(self):
        self.pack_forget()
        switchWindows.MainToSF(self.master)


if __name__ == "__main__":
    app = ttk.Window(
        title="CloudClientDemo",
        size=(900, 600),
        resizable=(False, False)
    )
    MainUI(app)
    app.mainloop()
