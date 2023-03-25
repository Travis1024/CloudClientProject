import os
import paramiko
import config


class SCPTransmitter():
    def __init__(self):

        self.hostname = config.getConfig("SFTP", "host")
        self.user = config.getConfig("SFTP", "user")
        self.password = config.getConfig("SFTP", "password")

        self.local_path = config.getConfig("SFTP", "localpath")
        self.remote_path = config.getConfig("SFTP", "remotepath")

        self.scp = paramiko.Transport(self.hostname, 22)
        self.scp.connect(username=self.user, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.scp)

    '''
        filename为文件名称的密文
        存放路径为下载路径
    '''
    def download(self, filename):
        try:
            remote_file = str(self.remote_path + filename)
            local_file = str(self.local_path + filename)
            self.sftp.get(remote_file, local_file)
            print("Successfully")
            self.sftp.close()
            self.scp.close()
        except IOError:
            print("self.remote_path or local_path is not exist")
            self.sftp.close()
            self.scp.close()
            return False
        return True


    '''
        localfile为文件的绝对路径
    '''
    def upload(self, localfile):
        try:
            filename = localfile[localfile.rfind('/') + 1:]
            self.sftp.put(localfile, str(self.remote_path + filename))
            print("Successfully")
            self.sftp.close()
            self.scp.close()
        except Exception as e:
            print(e)
            print("self.remote_path or local_path is not exist")
            self.sftp.close()
            self.scp.close()
            return False
        return True


if __name__ == "__main__":
    localfile = '/Users/travis/PycharmProjects/CloudClientProject/testdata/first.txt'
    transmitter = SCPTransmitter()
    transmitter.upload(localfile)
