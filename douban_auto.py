#-*-coding:utf-8-*-

import urllib
import urllib2
import re
import sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class Douban_auto:
    def __init__(self):
        self.content1=[]
        self.content2=[]
        self.content3=[]
        self.content4=[]
        self.content5=[]
        self.number=0
        self.tag_list=[]
        self.file=None
        self.Url=None
        self.type=None
        self.p=re.compile("\d+")
        self.headers={'User-Agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        self.pa_book=re.compile('<li class="subject-item">.*?<div class="info">.*?title=(.*?) onclick.*?<div class="pub">(.*?)</div>.*?<span class="rating_nums">(.*?)</span>.*?<span class="pl">(.*?)</span',re.S)
        self.pa_url=re.compile('<span class="next">.*?<link rel="next" href="(.*?)"/>.*?<a href',re.S)
       # self.pa_movie=re.compile('<table width="100%" class="">.*?<div class="pl2">.*?class="">(.*?)</a><p class="pl">(.*?)</p>.*? <span class="rating_nums">(.*?)</span>.*?<span class="pl">(.*?)</span>',re.S)
        self.pa_movie=re.compile('<table width="100%" class="">.*?title="(.*?)">.*?<p class="pl">(.*?)</p>.*? <span class="rating_nums">(.*?)</span>.*?<span class="pl">(.*?)</span>',re.S)
    def start(self):
        #books search
        book_num=0
        try:
            page_num=1
            self.type="book"
            self.Url=self.get_base_url()
            self.get_tags()
            for tag in self.tag_list:
                print(tag)
                book_url=self.get_url(tag)
                print("loading books : webpage "+str(page_num))
                page_num+=1
                print(book_url)
                while(book_url):
                    print(book_url)
                    book_url=self.get_book_contents(book_url)
            self.set_file()
            self.write_file()
            print("\nbooks complete! now movies begin\n")
            book_num=self.number
            self.__init__()
            #movies search
            page_num2=1
            self.type="movie"
            self.Url=self.get_base_url()
            self.get_tags()
            for tag in self.tag_list:
                print(tag)
                movie_url=self.get_url(tag)
                print("loading movies : webpage"+str(page_num2))
                page_num2+=1
                print(movie_url)
                while(movie_url):
                    movie_url=self.get_movie_contents(movie_url)
                    print(movie_url)
            self.set_file()
            self.write_file()
        except IOError,e:
            print("error"+e.message)
        finally:
            print(str(book_num)+" books are loaded \n"+str(self.number)+"  movies are loaded")

    def get_base_url(self):
        return "https://"+self.type+".douban.com/tag/"

    def get_tags(self):
        try:
           web_response=urllib2.urlopen(urllib2.Request(self.Url))
           web_contents=web_response.read().decode("utf-8")
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print u"failed",e.reason
                sys.exit()
        r=re.compile('<td><a href="/tag/.*?">(.*?)</a><b>.',re.S)
        results=re.findall(r,web_contents)
        for i in results:
            i=i.encode("utf-8")
            self.tag_list.append(i)

    def get_url(self,tag):
        return "https://"+self.type+".douban.com/tag/"+tag

    def get_book_contents(self,book_url):
        g=""
        t = 0
        while(g==""):
            try:
                req=urllib2.Request(book_url,headers=self.headers)
                response=urllib2.urlopen(req,timeout=3)
                g=response.read().decode("utf-8")
                t+=1
            except Exception, x:
                print("connect failed!try again...")
                if (t >= 10):
                    break
                pass
        result=re.findall(self.pa_book,g)
        for i in result:
            self.book_format(i)
        temp_url=self.pa_url.search(g)
        if temp_url==None:
            book_url=None
        elif temp_url.group(1).find("http")!=-1:
            book_url=temp_url.group(1)
        else:
            book_url="http://book.douban.com"+temp_url.group(1).encode("utf-8")
        return book_url

    def book_format(self,i):
        lis=[]
        for j in range(4):
            lis.append(i[j])
        lis[0]=lis[0].strip()+"      "
        lis[1]=lis[1].strip()
        lis[3]=lis[3].strip()
        lis.append("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        lis.insert(2,"\n    ")
        lis.insert(4,"    ")
        peo_num=self.p.search(lis[5])
        if (int(peo_num.group(0))>=2222):
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
        elif  (int(peo_num.group(0))<2222):
            self.book_append_in(lis, self.content5)
        else:
            print("hello ")

    def book_append_in(self,lis,content):
        self.number+=1
        str=""
        for count in range(7):
            str+=lis[count].encode("utf-8")
        content.append(str)

    def get_movie_contents(self,movie_url):
        g=""
        t=0
        while(g==""):
            try:
                req=urllib2.Request(movie_url,headers=self.headers)
                response=urllib2.urlopen(req,timeout=3)
                g=response.read().decode("utf-8")
                t+=1
            except Exception, x:
                print("connect failed!try again...")
                if t<=10:
                    break
                pass
        result=re.findall(self.pa_movie,g)
        for i in result:
            self.movie_format(i)
        temp_url=self.pa_url.search(g)
        if temp_url==None:
            movie_url=None
        elif temp_url.group(1).find("http")!=-1:
            movie_url=temp_url.group(1)
        else:
            movie_url="http://book.douban.com"+temp_url.group(1).encode("utf-8")
        return movie_url

    def movie_format(self,i):
        lis=[]
        for j in range(4):
            lis.append(i[j])
        lis[0]=lis[0]+"\n"
        lis[1]=lis[1]+"\n  评分 "
        lis[2]=lis[2]+"     "
        lis[3]+="\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        peo_num=self.p.search(lis[3])
        if (int(peo_num.group(0))>=3333):
            if( float (lis[2])>=8.5):
                self.movie_append_in(lis,self.content1)
            elif ( float (lis[2])>=8.0 ):
                self.movie_append_in(lis,self.content2)
            elif ( float (lis[2])>=7.5 ):
                self.movie_append_in(lis,self.content3)
            elif ( float(lis[2])>=7.0 ):
                self.movie_append_in(lis,self.content4)
            else :
                self.movie_append_in(lis,self.content5)
        else:
            self.movie_append_in(lis, self.content5)

    def movie_append_in(self,lis,content):
        self.number+=1
        str=""
        for count in range(4):
            str+=lis[count].encode("utf-8")
        content.append(str)


    def set_file(self):
        filename="douban_"+self.type+"_all.txt"
        self.file=open(filename,"w+")

    def write_file(self):
        self.content1=list(set( self.content1))
        self.content2=list(set( self.content2))
        self.content3=list(set( self.content3))
        self.content4=list(set( self.content4))
        self.content5=list(set( self.content5))
        self.file.write("\n\nlevel 1  (>9.0 for books)  (>8.5 for movies) \n\n")
        for item in self.content1:
            self.file.write(str(item))
        self.file.write("\n\nlevel 2  (>8.5 for books)  (>8.0 for movies) \n\n")
        for item in self.content2:
            self.file.write(str(item))
        self.file.write("\n\nlevel 3  (>8.0 for books)  (>7.5 for movies) \n\n")
        for item in self.content3:
            self.file.write(str(item))
        self.file.write("\n\nlevel 4  (>7.5 for books)  (>7.0 for movies) \n\n")
        for item in self.content4:
            self.file.write(str(item))
        self.file.write("\n\nlevel 5  (others) \n\n")
        for item in self.content5:
            self.file.write(str(item))


a=Douban_auto()
a.start()
