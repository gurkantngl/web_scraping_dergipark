from django.shortcuts import render

def search(request):
    print("search çalıştı")
    return render(request, 'article_page.html')

