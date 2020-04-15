from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
result = []
# Create your views here.
def home(request):
    query = request.GET.get('query','')
    if query == '':
        return render(request, 'searcher/index.html',{'display': False, 'query':query})
    else:
        result = search(query)
        return render(request, 'searcher/index.html', {'bookDic': result, 'display':True, 'query':query})

def book(request, book_id):
    downloadUrl = downloadBook('https://www.pdfdrive.com/a-e' + str(book_id) + '.html')
    return render(request, 'searcher/book.html',{'result':downloadUrl})

class Book:
    def __init__(self, name, image, year, size, pages,book_id, desc,author):
        self.name = name
        self.image = image
        self.size = size
        self.pages = pages
        self.book_id = book_id
        self.year = year
        self.author = author
        self.desc = desc

def search(query):
    array = list(query.split())
    searchUrl = "https://www.pdfdrive.com/search?q="+array[0]
    for i in range(1, len(array)):
        searchUrl = searchUrl + '+' + array[i]
    res = requests.get(searchUrl)
    soup = BeautifulSoup(res.text, 'lxml')
    bookList = soup.find_all('div', class_='col-sm', limit=10)
    resultArray = []
    for i in bookList:
        imgLink = i.find('img', class_='file-img')['src']
        book_id = i.find('a')['data-id']
        bookName = i.find('h2').text
        spans = i.find_all('span')
        pages = spans[1].text
        year = spans[3].text
        size = spans[5].text
        desc = str(i.find('div', class_='file-right').text).split('\n')[-2]
        newBook = Book(name=bookName, image=imgLink, size=size, pages=pages, book_id=book_id,year=year,desc=desc, author='')
        resultArray.append(newBook)
    return resultArray


def downloadBook(bookUrl):
    res = requests.get(bookUrl).text
    soup = BeautifulSoup(res, 'lxml')
    t = bookUrl.split('-')[-1]
    bookId = t[1: len(t) - 5]
    session = session_finder(str(res))
    downloadUrl = "https://www.pdfdrive.com/download.pdf?id=" + bookId + "&h=" + session + "&u=cache"
    main_book = soup.find_all('div', class_='ebook-main')[0]
    imgLink = main_book.find('img', class_='ebook-img')['src']
    bookName = main_book.find('h1').text
    spans = main_book.find_all('span')
    pages = spans[0].text
    year = spans[2].text
    size = spans[4].text
    authors = main_book.find_all('span', {'itemprop': "creator"})
    for i in range(len(authors)):
        authors[i] = authors[i].text

    result = Book(name=bookName, image=imgLink, size=size, pages=pages, book_id=downloadUrl, desc='',year=year, author=(', ').join(authors))
    return result

def session_finder(k):
    idx = k.find('session')
    p = k[idx+8:idx + 60]
    notFound = True
    session = ''
    i = 0
    p.replace("'", "")
    p.replace('"', '')
    while notFound:
        session += p[i]
        if p[i+1] == '"' or p[i+1] in "' ":
            notFound = False
        i += 1
    return session