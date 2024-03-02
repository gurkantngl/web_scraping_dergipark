import scrapy
import re

class ArticlesSpider(scrapy.Spider):
    name = "articles"
    allowed_domains = ["dergipark.org.tr"]
    start_urls = ["https://dergipark.org.tr/tr/search?q="]
    print("Aranacak anahtar kelimeyi girin: ")
    keyword = input()
    start_urls[0] += keyword
    
    print(start_urls)

    
    def parse(self, response):
        links = response.xpath("//div[@class='card article-card dp-card-outline']")
        wrong = response.xpath("//div[@class='alert-text']/p[1]//text()").getall()
        wrong = ' '.join(wrong)
        
        yield{
            "wrong" : wrong,
            "len" : len(links),
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
                
            yield{
                "count" : count,
                "type" : article_type,
                "title" : title,
                "link" : url,
                "authors" : authors,
                "date" : date,
                "publisher" : publisher,
                "doi" : doi,
            }
            
            yield scrapy.Request(url, callback=self.parse_article)
    
    def parse_article(self, response):
            title = response.xpath("//h3[@class='article-title']/text()").getall()
            title = ' '.join(title).strip()
            title = title.replace("\n","")
            
            abstract = response.xpath("//div[@class='article-abstract data-section']//p//text()").getall()
            abstract = ' '.join(abstract).strip()
            abstract = abstract.replace("\n","").replace("\r","")
            
            keywords = response.xpath("//div[@class='article-keywords data-section']/p//text()").getall()
            keywords = [keyword.strip() for keyword in keywords if len(keyword.strip())!=0 and keyword not in ',']             
            keywords = [word.split(';') if ";" in word else word for word in keywords ] 
        
            yield{
                "title" : title,
                "keywords" : keywords,
                "abstract" : abstract,
            }            
             