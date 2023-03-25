import base64
import datetime
import shutil
import cv2
import pymysql
import config
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import os
from SCPTransmitter import SCPTransmitter

class EnAndDecrypt:
    def __init__(self, path, keywords):
        self.filename = None
        self.path = path
        self.db = None
        self.filetype = None
        self.keywords = keywords

    def connectDB(self):
        try:
            self.db = pymysql.connect(
                host=config.getConfig("database", "host"),
                port=int(config.getConfig("database", "port")),
                user=config.getConfig("database", "user"),
                password=config.getConfig("database", "password"),
                database=config.getConfig("database", "dbname"),
                charset=config.getConfig("database", "charset"),
                autocommit=True
            )
        except Exception as e:
            print("数据库连接失败！！！")
            print(e)
            return False
        print("数据库连接成功！")
        return True


    def judgeType(self):
        rindex = str(self.path).rfind('/')
        if rindex == -1:
            rindex = 0
        self.filename = str(self.path)[rindex + 1:]

        if self.filename.endswith('txt'):
            self.filetype = "txt"
        elif self.filename.endswith('png'):
            self.filetype = "png"
        elif self.filename.endswith('jpg'):
            self.filetype = "jpg"
        elif self.filename.endswith('jpeg'):
            self.filetype = "jpeg"
        else:
            return False
        return True

    def startEncrypt(self):
        if str(self.filetype) == "txt":
            self.encryptText()
        else:
            self.encryptPicture()

    def encryptPicture(self):
        imgpath = self.path
        img = cv2.imread(imgpath)
        h, w, c = img.shape

        keyimage1 = cv2.imread("SecretKey/key1.png")
        keyimage2 = cv2.imread("SecretKey/key2.png")
        keyimage3 = cv2.imread("SecretKey/key3.png")
        keyimage4 = cv2.imread("SecretKey/key4.png")
        keyimage5 = cv2.imread("SecretKey/key5.png")

        key1 = cv2.resize(keyimage1, (w, h), interpolation=cv2.INTER_LINEAR)
        key2 = cv2.resize(keyimage2, (w, h), interpolation=cv2.INTER_LINEAR)
        key3 = cv2.resize(keyimage3, (w, h), interpolation=cv2.INTER_LINEAR)
        key4 = cv2.resize(keyimage4, (w, h), interpolation=cv2.INTER_LINEAR)
        key5 = cv2.resize(keyimage5, (w, h), interpolation=cv2.INTER_LINEAR)

        encryption1 = cv2.bitwise_xor(img, key1)
        encryption2 = cv2.bitwise_xor(encryption1, key2)
        encryption3 = cv2.bitwise_xor(encryption2, key3)
        encryption4 = cv2.bitwise_xor(encryption3, key4)
        result = cv2.bitwise_xor(encryption4, key5)

        prefix = imgpath[:imgpath.rfind('/')]
        imgname = imgpath[imgpath.rfind('/') + 1:]

        # 保存加密后的图片
        imgpath1 = str(prefix + "/copycopycopycopy." + self.filetype)
        cv2.imwrite(imgpath1, result)
        newname = self.enAESFileName(imgname)
        imgpath2 = str(prefix + "/" + newname)
        os.rename(imgpath1, imgpath2)

        # 计算文件大小
        stats = os.stat(imgpath2)
        filesize = self.convert_size(stats.st_size)

        # 将记录写入数据库
        cursor = self.db.cursor()
        sql_getCount = "SELECT COUNT(*) FROM filelist"
        cursor.execute(sql_getCount)
        count = int(cursor.fetchone()[0]) + 1
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 写入第一个表
        sql = "INSERT INTO filelist(idname, filename, uploadtime, filesize) VALUES ('{}', '{}', '{}', '{}')"
        sql1 = sql.format(count, newname, dt, filesize)
        cursor.execute(sql1)

        # 写入第二个表，需要对关键字加密,对count加密
        sql3 = "INSERT INTO secondlist(idname, keywords) VALUES ('{}', '{}')"
        enCount = self.enAESFileName(str(count))
        enKeywords = self.enAESFileName(str(self.keywords))
        sql33 = sql3.format(enCount, enKeywords)
        cursor.execute(sql33)


        # keylist = str(self.keywords).split(';')
        # for key in keylist:
        #     sql2 = "SELECT COUNT(*) FROM indexlist WHERE keyword = '{}'"
        #     sql22 = sql2.format(key)
        #     cursor.execute(sql22)
        #     flag = int(cursor.fetchone()[0])
        #     if flag == 0:
        #         sql3 = "INSERT INTO indexlist(keyword, fileidname) VALUES ('{}', '{}')"
        #         sql33 = sql3.format(key, str(count))
        #         cursor.execute(sql33)
        #     else:
        #         sql2 = "SELECT fileidname FROM indexlist WHERE keyword = '{}'"
        #         sql22 = sql2.format(key)
        #         cursor.execute(sql22)
        #         fileidname = str(cursor.fetchone()[0])
        #         newfileidname = fileidname + "@" + str(count)
        #         sql4 = "UPDATE indexlist SET fileidname = '{}' WHERE keyword = '{}'"
        #         sql44 = sql4.format(newfileidname, key)
        #         cursor.execute(sql44)


        # 传输文件
        transmitter = SCPTransmitter()
        transmitter.upload(imgpath2)
        os.remove(imgpath2)


    def encryptText(self):
        in_file = open(self.path, 'rb')
        data = in_file.read()
        in_file.close()
        rindex = str(self.path).rfind('/')
        copyPath1 = str(self.path)[:rindex]

        # 创建副本文件，内容为密文
        copyPath2 = copyPath1 + "/copycopycopycopy.txt"
        shutil.copy(self.path, copyPath2)
        cipher1 = AES.new(
            config.getConfig("AES", "key").encode('utf8'),
            AES.MODE_CBC,
            config.getConfig("AES", "iv").encode('utf8')
        )
        ct = cipher1.encrypt(pad(data, 16))

        # 向副本文件中写入密文
        out_file = open(copyPath2, "wb")
        out_file.write(ct)
        out_file.close()

        # 将副本文件名称进行加密
        newFileName = str(self.enAESFileName(self.filename))
        newFilePath = str(copyPath1 + "/" +newFileName)
        os.rename(copyPath2, newFilePath)

        # 计算文件大小
        stats = os.stat(newFilePath)
        filesize = self.convert_size(stats.st_size)

        # 将记录写入数据库
        cursor = self.db.cursor()
        sql_getCount = "SELECT COUNT(*) FROM filelist"
        cursor.execute(sql_getCount)
        count = int(cursor.fetchone()[0]) + 1
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 写入第一个表
        sql = "INSERT INTO filelist(idname, filename, uploadtime, filesize) VALUES ('{}', '{}', '{}', '{}')"
        sql1 = sql.format(count, newFileName, dt, filesize)
        cursor.execute(sql1)

        # 写入第二个表，需要对关键字加密,对count加密
        sql3 = "INSERT INTO secondlist(idname, keywords) VALUES ('{}', '{}')"
        enCount = self.enAESFileName(str(count))
        enKeywords = self.enAESFileName(str(self.keywords))
        sql33 = sql3.format(enCount, enKeywords)
        cursor.execute(sql33)


        # keylist = str(self.keywords).split(';')
        # for key in keylist:
        #     sql2 = "SELECT COUNT(*) FROM indexlist WHERE keyword = '{}'"
        #     sql22 = sql2.format(key)
        #     cursor.execute(sql22)
        #     flag = int(cursor.fetchone()[0])
        #     if flag == 0:
        #         sql3 = "INSERT INTO indexlist(keyword, fileidname) VALUES ('{}', '{}')"
        #         sql33 = sql3.format(key, str(count))
        #         cursor.execute(sql33)
        #     else:
        #         sql2 = "SELECT fileidname FROM indexlist WHERE keyword = '{}'"
        #         sql22 = sql2.format(key)
        #         cursor.execute(sql22)
        #         fileidname = str(cursor.fetchone()[0])
        #         newfileidname = fileidname + "@" + str(count)
        #         sql4 = "UPDATE indexlist SET fileidname = '{}' WHERE keyword = '{}'"
        #         sql44 = sql4.format(newfileidname, key)
        #         cursor.execute(sql44)


        # 传输文件
        transmitter = SCPTransmitter()
        transmitter.upload(newFilePath)
        os.remove(newFilePath)

    '''
        加密文件名称
    '''
    def enAESFileName(self, filename):
        cipher = AES.new(
            config.getConfig("AES", "key").encode('utf8'),
            AES.MODE_CBC,
            config.getConfig("AES", "iv").encode('utf8')
        )
        namect = cipher.encrypt(pad(str(filename).encode('utf8'), 16))
        AES_en_str = base64.b64encode(namect)
        AES_en_str = AES_en_str.decode("utf8")
        AES_en_str = AES_en_str.replace('/', '-')
        return AES_en_str

    '''
        解密文件名称
    '''
    def deAESFileName(self, filename):
        filename = str(filename).replace('-', '/')
        namect = base64.b64decode(filename)
        cipher2 = AES.new(
            config.getConfig("AES", "key").encode('utf8'),
            AES.MODE_CBC,
            config.getConfig("AES", "iv").encode('utf8')
        )
        den_text = unpad(cipher2.decrypt(namect), 16)
        return str(den_text.decode('utf8'))

    # filename为密文名称
    def decryptPicture(self, filename):
        filepath = str(config.getConfig("SFTP", "localpath") + filename)
        truename = self.deAESFileName(filename)
        newfilepath = str(config.getConfig("SFTP", "localpath") + truename)
        os.rename(filepath, newfilepath)

        img = cv2.imread(newfilepath)
        h, w, c = img.shape

        keyimage1 = cv2.imread("SecretKey/key1.png")
        keyimage2 = cv2.imread("SecretKey/key2.png")
        keyimage3 = cv2.imread("SecretKey/key3.png")
        keyimage4 = cv2.imread("SecretKey/key4.png")
        keyimage5 = cv2.imread("SecretKey/key5.png")

        key1 = cv2.resize(keyimage1, (w, h), interpolation=cv2.INTER_LINEAR)
        key2 = cv2.resize(keyimage2, (w, h), interpolation=cv2.INTER_LINEAR)
        key3 = cv2.resize(keyimage3, (w, h), interpolation=cv2.INTER_LINEAR)
        key4 = cv2.resize(keyimage4, (w, h), interpolation=cv2.INTER_LINEAR)
        key5 = cv2.resize(keyimage5, (w, h), interpolation=cv2.INTER_LINEAR)

        decryption1 = cv2.bitwise_xor(img, key5)
        decryption2 = cv2.bitwise_xor(decryption1, key4)
        decryption3 = cv2.bitwise_xor(decryption2, key3)
        decryption4 = cv2.bitwise_xor(decryption3, key2)
        init_image = cv2.bitwise_xor(decryption4, key1)
        os.remove(newfilepath)
        cv2.imwrite(newfilepath, init_image)


    # filename为密文名称
    def decryptText(self, filename):
        filepath = str(config.getConfig("SFTP", "localpath") + filename)
        truename = self.deAESFileName(filename)
        newfilepath = str(config.getConfig("SFTP", "localpath") + truename)
        os.rename(filepath, newfilepath)
        in_file = open(newfilepath, 'rb')
        data = in_file.read()
        in_file.close()

        # 清空文件中的内容
        with open(newfilepath, 'w') as file:
            file.truncate(0)

        cipher3 = AES.new(
            config.getConfig("AES", "key").encode('utf8'),
            AES.MODE_CBC,
            config.getConfig("AES", "iv").encode('utf8')
        )
        text = unpad(cipher3.decrypt(data), 16)
        out_file = open(newfilepath, 'wb')
        out_file.write(text)
        out_file.close()

    def searchTableFirst(self):
        cursor = self.db.cursor()
        sql = "SELECT * FROM filelist"
        cursor.execute(sql)
        dataList = list(cursor.fetchall())
        newList = []
        for i in range(len(dataList)):
            j = list(dataList[i])
            j[2] = self.deAESFileName(str(j[2]))
            j[3] = str(j[3])
            newList.append(j)
        return newList

    def searchTableSecond(self):
        cursor = self.db.cursor()
        sql = "SELECT * FROM secondlist"
        cursor.execute(sql)
        dataList = list(cursor.fetchall())
        newList = []
        for i in range(len(dataList)):
            j = list(dataList[i])
            j[1] = self.deAESFileName(str(j[1]))
            j[2] = self.deAESFileName(str(j[2]))
            newList.append(j)
        return newList


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

    def downloadFile(self, fileName):
        de_filename = self.enAESFileName(fileName)
        scp = SCPTransmitter()
        if scp.download(de_filename):
            if str(fileName).endswith("txt"):
                self.decryptText(de_filename)
            else:
                self.decryptPicture(de_filename)
            return True
        return False

    def closeDB(self):
        if self.db is not None:
            self.db.close()
            self.db = None
        print("数据库已断开连接！")
