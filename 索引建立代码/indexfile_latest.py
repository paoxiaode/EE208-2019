# -*- coding:utf-8 -*-
#!/usr/bin/env python

INDEX_DIR = "IndexFiles.index"
from bs4 import BeautifulSoup
import jieba

import sys, os, lucene, threading, time
from datetime import datetime

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, TextField, IntField, DoubleField, StringField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, dataFilePath, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        writer = IndexWriter(store, config)

        self.indexDocs(dataFilePath, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, dataFilePath, writer):

        noIndexedString = FieldType()
        noIndexedString.setTokenized(False)
        noIndexedString.setIndexed(False)
        noIndexedString.setStored(True)

        with open(dataFilePath, 'r') as f:
            shopinfo = f.readlines()

        cnt = 0
        validnum = 0

        for script in shopinfo:
            cnt += 1
            print cnt
            script = script.strip().split('\t')
            if len(script) < 7:
                print "data incomplete."
                continue

            try:
                goodname, salenum, price, shopname, url, picturename, comment, historyprice = sentenceModify(script)
                print "adding", goodname

                goodname_s = unicode(goodname, 'utf8')
                seg_list_good = jieba.cut(goodname_s, cut_all=False)
                goodname_s = " ".join(seg_list_good)  # 默认模式

                shopname_s = unicode(shopname, 'utf8')
                seg_list_shop = jieba.cut(shopname_s, cut_all=False)
                shopname_s = " ".join(seg_list_shop)  # 默认模式

                shopnameField = Field("shopName", shopname, noIndexedString)
                shopnameField_s = TextField("shopName_s", shopname_s, Field.Store.NO)
                goodnameField = Field("goodName", goodname, noIndexedString)
                goodnameField_s = TextField("goodName_s", goodname_s, Field.Store.NO)
                salenumField = IntField("saleNum", salenum, Field.Store.YES)
                priceField = DoubleField("price", price, Field.Store.YES)
                urlField = Field("url", url, noIndexedString)
                pictureField = StringField("pictureName", picturename, Field.Store.YES)
                commentField = Field("comments", comment, noIndexedString)
                historyPriceField = Field("historyPrice", historyprice, noIndexedString)


                doc = Document()
                doc.add(shopnameField)
                doc.add(shopnameField_s)
                doc.add(goodnameField)
                doc.add(goodnameField_s)
                doc.add(salenumField)
                doc.add(priceField)
                doc.add(urlField)
                doc.add(pictureField)
                doc.add(commentField)
                doc.add(historyPriceField)

                writer.addDocument(doc)
                validnum += 1
            except Exception, e:
                print "Failed in indexDocs:", e

        print "ValidNum:%s" % validnum


def sentenceModify(datali):
    goodName = datali[0].strip()
    tmpsaleNum = datali[1]
    if tmpsaleNum != '':
        tmpsaleNum = datali[1][9:]
        if len(tmpsaleNum) > 3 and not tmpsaleNum[-1:].isdigit():
            tmpsaleNum = tmpsaleNum[:-3]
            print "tmpsaleNum is %s" % tmpsaleNum
            saleNum = int(float(tmpsaleNum) * 10000)
        else:
            print "tmpsaleNum is %s" % tmpsaleNum
            saleNum = int(tmpsaleNum)
    else:
        saleNum = 0
    price = float(datali[3].strip())
    shopName = datali[4].strip()
    url = datali[5].strip()
    picturename = valid_filename(datali[6].strip())

    return goodName, saleNum, price, shopName, url, picturename, "None", "None"


def valid_filename(s):
    s = 'http:' + s
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    fileFrom = 'data_v2_total.txt'
    try:
        IndexFiles(fileFrom, "index_latest")
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
        raise e
