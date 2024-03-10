from django.shortcuts import render
from django.http import HttpResponse
from scrapy.crawler import CrawlerProcess
from scholar.scholar.spiders import articles
from scrapy.utils.project import get_project_settings
from multiprocessing import Process

def run_scrapy(input_words):
    process = CrawlerProcess(get_project_settings())
    process.crawl(articles.ArticlesSpider, keyword=input_words)
    process.start()
    process.join()

def search(request):
    print("search çalıştı")
    if request.method == 'POST':
        input_words = request.POST.get('inputWords', '')

        scrapy_process = Process(target=run_scrapy, args=(input_words,))
        scrapy_process.start()
        scrapy_process.join()

        return HttpResponse(f"Scraping yapılan keyword: {input_words}")
    
    else:
        return render(request, 'your_template.html')