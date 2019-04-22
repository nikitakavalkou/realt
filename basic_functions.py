import datetime
from urllib.request import Request, urlopen
import urllib.error
import pymongo
import time


class ScraperDB:

    def __init__(self,db_server, dbname):
        try:

            self.db_client = pymongo.MongoClient(db_server)
            self.db = self.db_client[dbname]
            self.db_server=db_server
        except:

            print("ScraperDB DB open error " + str(
                datetime.datetime.now()) + " db_name:" + dbname + " db_server: " + db_server)

    def DBPutObject(self, collection_name, dict_obj):
        try:
            mycol = self.db[collection_name]
            mycol.insert_one(dict_obj)
        except:
            print("DBPutObject() DB open error " + str(
                datetime.datetime.now()) + " server: " + self.db_server + " col_name:" + collection_name)
    def Collection(self,name):
        return self.db[name]




# Расстояние_Левенштейна

def LivenstainDistance(a, b):
    # "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


# Коэффициент Жаккара (частное — коэф. Танимото)

def tanimotok(s1, s2):
    a, b, c = len(s1), len(s2), 0.0

    for sym in s1:
        if sym in s2:
            c += 1

    return c / (a + b - c)


def clearString(str1):
    str1 = str1.replace('\r', '').replace('\n', '').replace('\t', '').replace('(', ' ')
    str1 = str1.replace(')', ' ').replace(',', ' ').replace('.', '').replace('-', ' ')
    str1 = str1.replace('  ', '').lower().strip()
    return str1


def compareWords(str1, str2):
    len1 = len(str1)
    len2 = len(str2)
    maxLen = max(len1, len2)
    averageLen = (len1 + len2) / 2
    return ((maxLen - LivenstainDistance(str1, str2)) / maxLen)


def compareStrings(str1, str2, c):
    result = []
    wordResult = []
    lastResult = 0

    for word1 in str1.split(' '):
        lastResult = 0
        for word2 in str2.split(' '):
            compResult = compareWords(word1, word2)
            if compResult > lastResult:
                lastResult = compResult
        if lastResult != 0 and lastResult >= c:
            result.append(lastResult)

    return result


def countWords(str1):
    text = str1.strip()
    text = text.rstrip()
    c = 0
    for word in text.split(' '):
        c = c + 1
    return c


def DBPutLogMessage(message):
    try:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["global"]
        mycol = mydb["log"]

        msg = {"time": datetime.datetime.now(), "msg": message}
        mycol.insert_one(msg)
    except:
        print("DBPutLogMessage() DB open error  " + str(datetime.datetime.now()))


def DBPutObject(db_client,db_name, collection_name, dict_obj):
    try:
        mydb = db_client[db_name]
        mycol = mydb[collection_name]
        mycol.insert_one(dict_obj)
    except:
        print("DBPutObject() DB open error " + str(datetime.datetime.now())+ " db_name:"+db_name+ " col_name:"+collection_name)


def GetPageText(url):
    # Gets URL as text, return URL contenet as text,
    # in case of HTML error returns Error code
    # in case of non-HTML error retuens None
    ErrorCount = 0
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    for i in range(0, 3):

        try:
            response = urlopen(req)
        except urllib.error.HTTPError as e:
            ExceptionMessage("HTTP ERROR: " + str(e.code) + " " + url)
            time.sleep(5)
            ErrorCount = ErrorCount + 1
            pass
        except Exception as e1:
            ExceptionMessage("HTTP ERROR:"+str(e1))
            time.sleep(5)
            ErrorCount = ErrorCount + 1
            pass
    if ErrorCount == 3:
        return None
    else:
        response.encoding = 'UTF-8'
        data = response.read()
        encoding = response.headers.get_content_charset('utf-8')

        return data.decode(encoding, errors='ignore')


def ExceptionMessage(command):
    DBPutLogMessage(command)
    print(command)

