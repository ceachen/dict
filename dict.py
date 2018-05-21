#!/usr/bin/env python

import sys
import json
import requests
import pymysql

"""
dict - Chinese/English Translation
@author Feei(wufeifei@wufeifei.com)
@date   2013.12.09
"""
dictDb = {"host": "127.0.0.1",
          "port": "3306",
          "user": "root",
          "passwd": "Hobot123456!",
          "db": "english_dict",
          "charset": "utf8"}


class Dict:
    key = '716426270'
    keyFrom = 'wufeifei'
    api = 'http://fanyi.youdao.com/openapi.do?keyfrom=wufeifei&key=716426270&type=data&doctype=json&version=1.1&q='
    content = None
    askWord = ""

    def __init__(self, argv):
        if len(argv) == 1:
            self.askWord = argv[0]
            if self.askWord.isalpha():
                self.en2cn_flag = True
            self.conn = pymysql.connect(host=dictDb["host"], port=dictDb["port"], user=dictDb["user"], passwd=dictDb["passwd"],
                                   db=dictDb["db"], charset=dictDb["charset"], unix_socket="/var/lib/mysql/mysql.sock")
            self.cur = self.conn.cursor()
            self.myFind()
            self.release()
        else:
            print("ERROR. usage: dict word")

    def myFind(self):
        if not self.local_find():
            self.api = self.api + self.askWord

            content = requests.get(self.api).text
            self.content = json.loads(content)
            self.update_local()

        self.parse()

    def parse(self):
        code = self.content['errorCode']

        if code == 0:  # Success
            try:
                u = self.content['basic']['us-phonetic']  # English
                e = self.content['basic']['uk-phonetic']
            except KeyError:
                try:
                    c = self.content['basic']['phonetic']  # Chinese
                except KeyError:
                    c = 'None'
                u = 'None'
                e = 'None'

            try:
                explains = self.content['basic']['explains']
            except KeyError:
                explains = 'None'

            print('- '*40)
            print(" %s, %s" % (self.content['query'], self.content['translation'][0]))
            if u != 'None':
                print('(U:', u, 'E:', e, ')')
            elif c != 'None':
                print('(Pinyin:', c, ')')
            else:
                print()

            if explains != 'None':
                for i in range(0, len(explains)):
                    print('', explains[i])
            else:
                print('Explains None')
            print('- '*40)

        elif code == 20:  # Text to long
            print('WORD TO LONG')
        elif code == 30:  # Trans error
            print('TRANSLATE ERROR')
        elif code == 40:  # Don't support this language
            print('CAN\'T SUPPORT THIS LANGUAGE')
        elif code == 50:  # Key failed
            print('KEY FAILED')
        elif code == 60:  # Don't have this word
            print('DO\'T HAVE THIS WORD')


    def local_find(self):

        if self.en2cn_flag:
            sqlCmd = "SELECT * FROM en2cn_tbl WHERE word = \"" + self.askWord + "\""
        else:
            sqlCmd = "SELECT * FROM cn2en_tbl WHERE word = \"" + self.askWord + "\""

        self.cur.execute(sqlCmd)
        # print(self.cur.fetchone())
        if self.cur.rowcount == 0:
            # //cur.close()
            # //conn.close()
            return False
        self.content = self.cur.fetchone()
        return True

    def update_local(self):
        if self.en2cn_flag:
            # sqlCmd = "INSERT INTO en2cn_tbl(word, explain) VALUES(\"" + self.askWord + "\", \"" + str(self.content) + "\""
            pass
        else:
            pass
            # sqlCmd = "INSERT INTO cn2en_tbl(word, explain) VALUES(\"" + self.askWord + "\", \"" + str(self.content) + "\""

        # self.cur.execute(sqlCmd)
        # self.conn.commit()

    def release(self):
        self.cur.close()
        self.conn.close()


if __name__ == '__main__':
    Dict(sys.argv[1:])
