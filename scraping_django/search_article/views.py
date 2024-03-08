from django.shortcuts import render
from django.http import HttpResponse
import subprocess

def search(request):
    print("search çalıştı")
    if request.method == 'POST' :
        print("POST çalıştı")
        input_words = request.POST.get('inputWords', '')
        print("input_words: ", input_words)
        
        scrapy_command = f"scrapy crawl your_spider_name -a input_words={input_words}"

        # Shell komutunu çalıştırın
        process = subprocess.Popen(scrapy_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        # scrapy dosyasının çıktısını HttpResponse ile gönderin
        return HttpResponse(f"Scrapy output: {output.decode('utf-8')}")
    else:
        # Form sayfasını göster
        return render(request, 'your_template.html')

