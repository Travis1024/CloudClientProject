import datetime
import pathlib
from queue import Queue
from threading import Thread
from tkinter.filedialog import askdirectory

import ttkbootstrap
import ttkbootstrap as ttk
from ttkbootstrap import Scrollbar
from ttkbootstrap.constants import *
from ttkbootstrap import utility
import switchWindows
from SearchEncrypt import txt2array, Reader, YunF, File, Publisher
from enAndDecrypt import EnAndDecrypt


class SearchFiles(ttk.Frame):

    queue = Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=(40, 20))
        self.mainUIPage = None
        self.pack(fill=BOTH, expand=YES)

        self.create_header()

        # application variables
        self.keywords_var = ttk.StringVar(value='Enter the keywords you want to search, separated by ";"')
        self.term_var = ttk.StringVar(value='txt')
        self.type_var = ttk.StringVar(value='Contains')

        # self.labelTitle = ttk.Label(text="Search-Files")
        # self.labelTitle.pack(fill=X, expand=YES, anchor=N)

        # header and labelframe option container
        option_text = "Complete the form to begin your search"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.xscroll = Scrollbar(self, orient=HORIZONTAL)
        self.yscroll = Scrollbar(self, orient=VERTICAL)

        self.create_keywords_row()
        self.create_term_row()
        self.create_type_row()
        self.create_results_view()



    def create_header(self):
        labelTitle = ttk.Label(
            master=self,
            text="Files-Search",
            bootstyle=(SUCCESS, INVERSE),
            padding=10,
        )
        labelTitle.pack(fill=X, expand=YES, pady=10)

    def create_keywords_row(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="Keywords", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.keywords_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        back_btn = ttk.Button(
            master=path_row,
            text="Return",
            command=self.on_back,
            bootstyle=(WARNING, OUTLINE),
            width=8
        )
        back_btn.pack(side=LEFT, padx=5)


    def create_term_row(self):
        """Add term row to labelframe"""
        term_row = ttk.Frame(self.option_lf)
        term_row.pack(fill=X, expand=YES, pady=15)
        term_lbl = ttk.Label(term_row, text="Term", width=8)
        term_lbl.pack(side=LEFT, padx=(15, 0))
        term_ent = ttk.Entry(term_row, textvariable=self.term_var)
        term_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        search_btn = ttk.Button(
            master=term_row,
            text="Search",
            command=self.on_search,
            bootstyle=OUTLINE,
            width=8
        )
        search_btn.pack(side=LEFT, padx=5)

    def create_type_row(self):
        """Add type row to labelframe"""
        type_row = ttk.Frame(self.option_lf)
        type_row.pack(fill=X, expand=YES)
        type_lbl = ttk.Label(type_row, text="Type", width=8)
        type_lbl.pack(side=LEFT, padx=(15, 0))

        contains_opt = ttk.Radiobutton(
            master=type_row,
            text="Contains",
            variable=self.type_var,
            value="contains"
        )
        contains_opt.pack(side=LEFT)
        contains_opt.invoke()

        refresh_btn = ttk.Button(
            master=type_row,
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

    def on_search(self):
        """Search for a term based on the search type"""
        # search_term = self.term_var.get()
        search_keywords = self.keywords_var.get()
        # search_type = self.type_var.get()
        # 通过关键字进行搜索
        searchkeylist = str(search_keywords).split(';')
        sk1 = txt2array("SecretKey/SK1.txt", " ")
        sk2 = txt2array("SecretKey/SK2.txt", " ")
        sk3 = txt2array("SecretKey/SK3.txt", " ")[0]

        getclass = EnAndDecrypt("NULL", "NULL")
        getclass.connectDB()
        secondList = getclass.searchTableSecond()
        dataList = getclass.searchTableFirst()
        filenames = []
        W = []

        for i in range(len(secondList)):
            j = secondList[i]
            filenames.append(j[1])
            keylist = str(j[2]).split(';')
            W.append(keylist)

        files = [File(filename) for filename in filenames]

        # 每个文件插入关键词
        for idx, f in enumerate(files):
            f.ninsert(W[idx])
            f.getWordsBytes()


        # 发布者将文件记录下来
        publisher = Publisher(files, sk1, sk2, sk3)

        # 发布者将安全索引和数据发送到YunF
        # indexID = 【安全索引，文档ID集（全部是hash后的值）】
        indexIDs = publisher.package()

        reader = Reader(sk1, sk2, sk3)
        # 访问者设置查询关键词
        reader.setQuery(searchkeylist)
        # 访问者生成陷门
        t_1, t_2 = reader.TrapDoor()

        # 服务器根据陷门可以得到查询结果
        server = YunF(indexIDs)
        dictTemp = server.calcuQuery(t_1, t_2)

        temp_dict = {}
        for temp in dictTemp:
            for indexStr in dictTemp.get(temp):
                # print(temp_dict.get(indexStr))
                if temp_dict.get(indexStr) is None:
                    temp_dict[indexStr] = float(temp)
                else:
                    temp_dict[indexStr] = float(temp_dict.get(indexStr)) + float(temp)

        res_list = sorted(temp_dict.items(), key=lambda x: x[1], reverse=True)

        resultList = []

        for i in range(len(res_list)):
            resultList.append(dataList[int(res_list[i][0]) - 1])

        x = self.resultview.get_children()
        if len(x) != 0:
            for item in x:
                self.resultview.delete(item)

        for i in range(len(resultList)):
            j = resultList[i]
            self.resultview.insert(
                parent='',
                index=END,
                values=(str(j[1]), str(j[2]), str(j[3]), str(j[4]))
            )


    def on_back(self):
        # start search in another thread to prevent UI from locking
        self.pack_forget()
        switchWindows.SFToMain(self.master)


    def convert_size(size):
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
        title="Files-Search",
        size=(900, 600),
        resizable=(False, False)
    )
    SearchFiles(app)
    app.mainloop()

