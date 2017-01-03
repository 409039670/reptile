#-*- coding:utf-8 -*-
import urllib
import urllib2
import re
import os
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class DouBan:
    def __init__(self,type="book",tag="小说"):
        self.tag=tag
        self.defaultName="douban_"+type+"_"+tag
        self.contents=[]
        self.content1=[] #>=9.0
        self.content2=[] #>=8.5
        self.content3=[] #>=8.0
        self.content4=[] #>=7.5
        self.content5=[] #<7.5 or not enough data(3333)
        self.number=0
        self.type=type
        self.Url=None
        self.pa_book=re.compile('<li class="subject-item">.*?<div class="info">.*?title=(.*?) onclick.*?<div class="pub">(.*?)</div>.*?<span class="rating_nums">(.*?)</span>.*?<span class="pl">(.*?)</span',re.S)
        self.pa_url=re.compile('<span class="next">.*?<link rel="next" href="(.*?)"/>.*?<a href=.*?>',re.S)
        self.pa_movie=re.compile('<table width="100%" class="">.*?title="(.*?)">.*?/ <span style="font-size:12px;">(.*?)</span>.*?<p class="pl">(.*?)</p>.*? <span class="rating_nums">(.*?)</span>.*?<span class="pl">(.*?)</span>',re.S)

    def start(self):
        page_num=1
        try:
            if self.type=="book":
                self.Url=self.getBaseUrl()
                self.get_book_contents()
                print("loading page:"+str(page_num))
                page_num+=1
                while(self.Url):
                    self.get_book_contents()
                    print("loading page:"+str(page_num))
                    page_num+=1
            elif self.type=="movie":
                self.Url=self.getBaseUrl()

                self.get_movie_contents()
                print("loading page:"+str(page_num))
                page_num+=1
                while(self.Url):
                    self.get_movie_contents()
                    print("loading page:"+str(page_num))
                    page_num+=1
            else:
                print("please input correct type")
                os._exit(1)
            self.setFile()
            self.writeFile()
        except IOError,e:
            print "write error, reason:"+e.message
        finally:
            print self.type+" "+self.tag+": "+str(self.number)+self.type+"s are loaded"
            print " write  complete"

    def setFile(self):
        self.fileName=self.defaultName+".txt"
        self.file=open(self.fileName,"w+")

    def getBaseUrl(self):
        BaseUrl="http://"+self.type+".douban.com/tag/"+self.tag+"?start="+"0"+"&type=T"
        return BaseUrl

    def get_book_contents(self):
        try:
            req=urllib2.Request(self.Url)
            response=urllib2.urlopen(req)
            g = response.read().decode("utf-8")
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print u"failed",e.reason
            os._exit(1)
        result=re.findall(self.pa_book,g)
        for i in result:
            self.book_format(i)
        temp_url=self.pa_url.search(g)
        if temp_url==None:
            self.Url=None
        elif temp_url.group(1).find("http")!=-1:
            self.Url=temp_url.group(1)
            print("hello")
        else:
            self.Url="http://book.douban.com"+temp_url.group(1).encode("utf-8")

    def get_movie_contents(self):
        try:
            req=urllib2.Request(self.Url)
            response=urllib2.urlopen(req)
            g = response.read().decode("utf-8")
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print u"failed",e.reason
            os._exit(1)
        result=re.findall(self.pa_movie,g)
        for i in result:
            self.movie_format(i)
        temp_url=self.pa_url.search(g)
        if temp_url==None:
            self.Url=None
        elif temp_url.group(1).find("http")!=-1:
            self.Url=temp_url.group(1)
        else:
            self.Url="http://book.douban.com"+temp_url.group(1).encode("utf-8")

    def writeFile(self):
        self.file.write("\n\nlevel 1  (>9.0) \n\n")
        for item in self.content1:
            self.file.write(str(item))
        self.file.write("\n\nlevel 2  (>8.5) \n\n")
        for item in self.content2:
            self.file.write(str(item))
        self.file.write("\n\nlevel 3  (>8.0) \n\n")
        for item in self.content3:
            self.file.write(str(item))
        self.file.write("\n\nlevel 4  (>7.5) \n\n")
        for item in self.content4:
            self.file.write(str(item))
        self.file.write("\n\nlevel 5  (others) \n\n")
        for item in self.content5:
            self.file.write(str(item))

    #输出书信息的格式
    def book_format(self,i):
        lis=[]
        for j in range(4):
            lis.append(i[j])
        lis[0]=lis[0].strip()+"  "
        lis[1]=lis[1].strip()
        lis[3]=lis[3].strip()
        lis.append("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        lis.insert(2,"\n    ")
        lis.insert(4,"    ")
        p=re.compile("\d+")
        peo_num=p.search(lis[5])
        if (int(peo_num.group(0))>=3333):
            if( float (lis[3])>=9.0):
                self.book_append_in(lis, self.content1)
            elif ( float (lis[3])>=8.5 ):
                self.book_append_in(lis,self.content2)
            elif ( float (lis[3])>=8.0 ):
                self.book_append_in(lis,self.content3)
            elif ( float(lis[3])>=7.5 ):
                self.book_append_in(lis,self.content4)
            else :
                self.book_append_in(lis,self.content5)
        else:
            self.book_append_in(lis, self.content5)

    def book_append_in(self,lis,content):
        self.number+=1
        for count in range(7):
            content.append(lis[count].encode("utf-8"))

    def movie_format(self,i):
        lis=[]
        for j in range(5):
            lis.append(i[j])
        lis.insert(1,"    又名：")
        lis.insert(3,"\n  ")
        lis.insert(5,"\n  ")
        lis.insert(7,"    ")
        lis.insert(9,"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        p=re.compile("\d+")
        peo_num=p.search(lis[8])
        if (int(peo_num.group(0))>=3333):
            if( float (lis[6])>=8.5):
                self.movie_append_in(lis,self.content1)
            elif ( float (lis[6])>=8.0 ):
                self.movie_append_in(lis,self.content2)
            elif ( float (lis[6])>=7.5 ):
                self.movie_append_in(lis,self.content3)
            elif ( float(lis[6])>=7.0 ):
                self.movie_append_in(lis,self.content4)
            else :
                self.movie_append_in(lis,self.content5)
        else:
            self.movie_append_in(lis, self.content5)

    def movie_append_in(self,lis,content):
        self.number+=1
        for count in range(10):
            content.append(lis[count].decode("utf-8"))
type=raw_input("movie or book?\n")
tag=raw_input("please select a tag:\n")
a=DouBan(type=type,tag=tag)
a.start()
