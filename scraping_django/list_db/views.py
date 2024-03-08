from django.shortcuts import render

def list_db(request):
    print("List db çalıştı")
    return render(request, 'article_page.html')
