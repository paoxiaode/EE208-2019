# -*- coding:utf-8 -*-
import urllib2
import os

def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

def writeImage(link):
    index_filename = '宠物清洁用品index.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = '宠物清洁用品'  # 存放网页的文件夹

    request = urllib2.Request(link)
    image = urllib2.urlopen(request).read()
    filename = valid_filename(link)  # 将网址变成合法的文件名
    index = open(index_filename, 'a')
    #index.write(link.strip('\n') + '\t' + filename + '\n')
    index.write('%s\t%s\n' % (filename,link.encode('ascii', 'ignore')))
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w')
    f.write(image)  # 将网页存入文件
    f.close()


if __name__ == "__main__":
    with open("宠物清洁用品.txt", 'r') as f:
        for line in f.readlines():
            lines = line.strip('\n')
            data = lines.split('\t')
            x = len(data)
            url = data[x-1]
            fullurl = 'http:'+ url
            writeImage(fullurl)
