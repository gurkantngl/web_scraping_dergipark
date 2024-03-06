from django.shortcuts import render

def search(request):
    print("çalıştı")
    return render(request, 'article_page.html')

