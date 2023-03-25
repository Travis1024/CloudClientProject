
import numpy as np
import pybloom_live


def txt2array(txt_path, delimiter):
    #---
    # 功能：读取只包含数字的txt文件，并转化为array形式
    # txt_path：txt的路径；delimiter：数据之间的分隔符
    #---
    data_list = []
    with open(txt_path) as f:
        data = f.readlines()
    for line in data:
        line = line.strip("\n")  # 去除末尾的换行符
        data_split = line.split(delimiter)
        temp = list(map(float, data_split))
        data_list.append(temp)

    data_array = np.array(data_list, dtype=int)
    return data_array


def getBloomBitArray(key):
    bf = pybloom_live.BloomFilter(capacity=80, error_rate=0.001)
    key = (bytes.decode(key, encoding="utf-8") + '#').encode(encoding="utf-8")
    for i in range(len(key) - 1):
        bf.add(key[i:i + 2])
    return np.array(bf.bitarray.tolist(), dtype='f4')




class File(object):
    def __init__(self, filename):
        self.filename = filename
        self.keywords = set()

    def ninsert(self, keywordsVec):
        for w in keywordsVec:
            self.keywords.add(w)

    def query(self, keyword):
        return self.keywords.__contains__(keyword)

    def getWordsBytes(self):
        return np.array([x.encode(encoding="utf-8") for x in self.keywords])


    def getHashID(self):
        return self.filename


class Publisher(object):
    def __init__(self, Files, sk1, sk2, sk3):
        self.M1 = sk1
        self.M2 = sk2
        self.S = sk3
        self.BF = None
        self.index = None
        self.files = Files

    def InvertIndex(self):
        self.index = {}
        self.BF = {}
        for f in self.files:
            fkey = f.getWordsBytes()
            for key in fkey:
                if key not in self.index.keys():
                    self.index[key] = set()
                    self.BF[key] = getBloomBitArray(key)
                self.index[key].add(f.getHashID())


    def package(self):
        # 生成倒排索引
        self.InvertIndex()
        # 生成安全索引
        self.SecureIndex()
        keys = self.index.keys()
        # 生成安全关键词和文档ID的索引包
        indexIDs = []
        for key in keys:
            indexIDs.append([self.secureIndex[key], self.index[key]])
        return indexIDs

    def SecureIndex(self):
        self.secureIndex = {}
        r = 8
        for key, B in self.BF.items():
            B_1 = np.zeros_like(B)
            B_2 = np.zeros_like(B)
            for j in range(B.shape[0]):
                if self.S[j] == 0:
                    B_1[j] = 0.5 * B[j] + r
                    B_2[j] = 0.5 * B[j] - r
                else:
                    B_1[j] = B[j]
                    B_2[j] = B[j]
            I_1 = self.M1.T @ B_1
            I_2 = self.M2.T @ B_2
            I_i = (I_1, I_2)
            self.secureIndex[key] = I_i
        return self.secureIndex



class Reader(object):
    def __init__(self, sk1, sk2, sk3):
        self.M1 = sk1
        self.M2 = sk2
        self.S = sk3

    def setQuery(self, query=None):
        queryBF = np.zeros_like(self.S)
        if query is None or len(query) == 0:
            return queryBF
        for q in query:
            qb = getBloomBitArray(q.encode(encoding="utf-8"))
            queryBF[qb > 0] = 1
        self.B = queryBF
        return queryBF

    def TrapDoor(self):
        r = 6
        B = np.copy(self.B)
        B_1 = np.zeros_like(B)
        B_2 = np.zeros_like(B)
        for j in range(len(B)):
            if self.S[j] == 0:
                B_1[j] = B[j]
                B_2[j] = B[j]
            else:
                B_1[j] = 0.5 * B[j] + r
                B_2[j] = 0.5 * B[j] - r

        t_1 = np.linalg.inv(self.M1) @ B_1
        t_2 = np.linalg.inv(self.M2) @ B_2
        return t_1, t_2


class YunF(object):
    def __init__(self, indexIDs):
        # indexIDs.append([self.secureIndex[key], self.index[key]])
        self.I = []
        self.ID = []
        for i, val in enumerate(indexIDs):
            index, ids = val
            self.I.append(index)
            self.ID.append(ids)

    def calcuQuery(self, t_1, t_2):
        queryRes = {}
        for idx, I in enumerate(self.I):
            I_1 = I[0]
            I_2 = I[1]
            queryRes[I_1.T @ t_1 + I_2.T @ t_2] = self.ID[idx]
        sort_key = sorted(queryRes.keys(), reverse=True)
        self.queryRes = {}
        for s in sort_key:
            if abs(s) < 1e-3:
                continue
            self.queryRes[s] = queryRes[s]
        return self.queryRes