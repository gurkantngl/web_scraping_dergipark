import scrapy
import re
from pymongo.mongo_client import MongoClient
from inline_requests import inline_requests
from scrapy.http import Request

client = MongoClient('127.0.0.1',27017)

db = client.Yazlab2

collection_name = db["Articles"]


class ArticlesSpider(scrapy.Spider):
    name = "articles"
    allowed_domains = ["dergipark.org.tr"]
    start_urls = ["https://dergipark.org.tr/tr/search?q="]
    print("Aranacak anahtar kelimeyi girin: ")
    keyword = input()
    start_urls[0] += keyword
    articles = {keyword:[]}
    articles2 = {keyword:[]}
    print(start_urls)
    count = 0
    count2 = 0
    
    @inline_requests
    def parse(self, response):
        result = collection_name.find_one({self.keyword:{"$exists": True}}) is not None
        if not result:
            links = response.xpath("//div[@class='card article-card dp-card-outline']")
            wrong = response.xpath("//div[@class='alert-text']/p[1]//text()").getall()
            wrong = ' '.join(wrong)
            
            self.count = len(links)
            
            yield{
                "wrong" : wrong,
                "keyword" : self.keyword
            }
            
            for link in links:
                title = link.xpath(".//div[@class='card-body']/h5[@class='card-title']/a[1]/text()").get().strip()
                url = link.xpath(".//div[@class='card-body']/h5[@class='card-title']/a[1]/@href").get().strip()
                
                count = len(link.xpath(".//div[@class='card-body']/h5//small").getall())
                
                article_type = "-"
                publisher = ""
                if count == 2:
                    article_type = link.xpath(".//div[@class='card-body']/h5/small[1]/span/text()").get()
                    textList = link.xpath(".//div[@class='card-body']/h5/small[2]//text()").getall()  
                else:
                    textList = link.xpath(".//div[@class='card-body']/h5/small[1]//text()").getall()
                
                str = ' '.join(textList)
                str = str.replace("\n","")
                str = str.strip()
                
                
                authors = str.split('(', 1)[0].strip().split(',')
                authors = [author.strip() for author in authors if len(author)!=0]
                
                publisher = re.search(r'\),\s*(.*?),', str)
                if publisher:
                    publisher = publisher.group(1).strip()
                
                
                date = re.search(r'\((.*?)\)', str)
                if date:
                    date = date.group(1)

                doi = link.xpath(".//a[starts-with(@href,'https://doi.org')]/text()").get()
                if doi is None:
                    doi = "-"
                    
                article = {
                    "type" : article_type,
                    "title" : title,
                    "link" : url,
                    "authors" : authors,
                    "date" : date,
                    "publisher" : publisher,
                    "doi" : doi,
                }
                
                self.articles[self.keyword].append(article)
                
            
                
                yield Request(url, callback=self.parse_article)
            

        else:
            print("this keyword is already in the database")
        
    def parse_article(self, response):
        title = response.xpath("//h3[@class='article-title']/text()").getall()
        title = ' '.join(title).strip()
        title = title.replace("\n","")
        
        abstract = response.xpath("//div[@class='article-abstract data-section']//p//text()").getall()
        abstract = ' '.join(abstract).strip()
        abstract = abstract.replace("\n","").replace("\r","")
        
        keywords = response.xpath("//div[@class='article-keywords data-section']//p//text()").get()
        keywords = [keyword.strip() for keyword in keywords if len(keyword.strip())!=0 and keyword not in ',']             
        keywords = [word.split(';') if ";" in word else word for word in keywords ] 
        references = response.xpath("//div[@class='article-citations data-section']/div/ul/li")
        referenceList = []
        for reference in references:
            ref = reference.xpath(".//text()").getall()
            ref = ' '.join(ref).strip()
            ref = ref.replace("\"","`").replace("\n","").replace("\r","").replace("\t","")
            referenceList.append(ref)
        
        article = {
            "title" : title,
            "references" : referenceList,
            "keywords" : keywords,
            "abstract" : abstract,
        } 
        
        print("=======================eklendi")
        self.articles2[self.keyword].append(article)
        
        self.count2+=1
        
        if self.count == self.count2:
            for i in self.articles[self.keyword]:
                for j in self.articles2[self.keyword]:
                    if i["title"] == j["title"]:
                        i.update(j)
                        break
            
            try:
                result = collection_name.insert_one(self.articles)
            except:
                print("===================================Error===============================")
            
        yield
    
    
    