#!/usr/bin/env python
# -*- coding: gbk -*-
import jieba

import sys, os, lucene, time, re
from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexReader, IndexWriterConfig, Term, DirectoryReader
from org.apache.lucene.document import Document, Field, FieldType, TextField, IntField, DoubleField, StringField
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, TermQuery
from org.apache.lucene.util import Version


class IndexUpdate(object):
    def __init__(self, storeDir):
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        print 'lucene', lucene.VERSION
        self.dir = SimpleFSDirectory(File(storeDir))

    # def getTxtAttribute(self, contents, attr):
    #     m = re.search(attr + ': (.*?)\n', contents)
    #     if m:
    #         return m.group(1)
    #     else:
    #         return ''

    def testDelete(self, fieldName, searchString):
        analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        writer = IndexWriter(self.dir, config)
        writer.deleteDocuments(Term(fieldName, searchString))
        writer.close()

    def testAdd(self, goodname, salenum, price, shopname, url, picturename, comment, historyprice):
        analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        writer = IndexWriter(self.dir, config)
        # True，建立新索引，False，建立增量索引

        noIndexedString = FieldType()
        noIndexedString.setTokenized(False)
        noIndexedString.setIndexed(False)
        noIndexedString.setStored(True)

        try:
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
        except Exception, e:
            print "Failed in indexDocs:", e

        writer.commit()
        writer.close()

    # def getHitCount(self, fieldName, searchString):
    #     reader = DirectoryReader.open(self.dir)  # readOnly = True
    #     print '%s total docs in index' % reader.numDocs()
    #
    #     searcher = IndexSearcher(reader)  # readOnly = True
    #     t = Term(fieldName, searchString)
    #     query = TermQuery(t)
    #     hitCount = len(searcher.search(query, 50).scoreDocs)
    #
    #     reader.close()
    #     print "%s total matching documents for %s\n---------------" \
    #           % (hitCount, searchString)
    #     return hitCount


def sentenceModify(datali):
    goodName = datali[0].strip()
    tmpsaleNum = datali[1]
    if tmpsaleNum != '':
        tmpsaleNum = datali[1][9:]
        if len(tmpsaleNum) > 3 and not tmpsaleNum[-1].isdigit():
            tmpsaleNum = tmpsaleNum[:-3]
            saleNum = int(float(tmpsaleNum) * 10000)
            print "saleNum is %s" % saleNum
        else:
            saleNum = int(tmpsaleNum)
            print "saleNum is %s" % saleNum
    else:
        saleNum = 0
    price = float(datali[3].strip())
    shopName = datali[4].strip()
    url = datali[5].strip()
    picturename = valid_filename(datali[6].strip())

    return goodName, saleNum, price, shopName, url, picturename, "CommentHere", "None"


def valid_filename(s):
    s = 'http:' + s
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


if __name__ == '__main__':
    index = IndexUpdate('index_latest')

    with open("complete.txt", 'r') as f:
        scripts = f.readlines()

    for script in scripts:
        script = script.strip().split('\t')
        url = script[3]
        picturename = script[0]
        goodname = script[4]
        shopname = script[2]
        salenum = int(script[1])
        price = float(script[6])
        historyprice = script[5]
        comment_file = eval(repr(url[:]).replace('/', '')) + '.txt'
        comment_file = '_'.join(comment_file.split('?'))
        comment_file = 'comment/http_' + comment_file

        try:
            with open(comment_file, 'r') as f:
                comment = f.read()
            print 'delete %s' % picturename
            index.testDelete('pictureName', picturename)

            print 'add %s' % picturename
            index.testAdd(goodname, salenum, price, shopname, url, picturename, comment, historyprice)
        except Exception, e:
            print "Failed: ", e

