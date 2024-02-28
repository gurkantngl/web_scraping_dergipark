import scrapy
import re

class ArticlesSpider(scrapy.Spider):
    name = "articles"
    allowed_domains = ["scholar.google.com"]
    start_urls = ["https://scholar.google.com/scholar?hl=tr&as_sdt=0%252C5&q="]
    print("Aranacak anahtar kelimeyi girin: ")
    keyword = input()
    start_urls[0] += keyword
    
    print(start_urls)

    def parse(self, response):
        links = response.xpath("//div[@id='gs_res_ccl_mid']/div[@class='gs_r gs_or gs_scl']/div[@class='gs_ri']")
        sperring_correction = response.xpath("//h2[@class='gs_rt']/text() | //h2[@class='gs_rt']/a/text() | //h2[@class='gs_rt']/a/b/i/text()").getall()
        sperring_correction = ' '.join(sperring_correction)
        yield{
            "sperring_correction" : sperring_correction
        }
        for link in links:
            title = link.xpath("string(.//h3[@class='gs_rt']/a)").get()
            url = link.xpath(".//h3[@class='gs_rt']/a/@href").get()
            author_ = link.xpath(".//div[@class='gs_a']/a/text() | .//div[@class='gs_a']/text()").getall()
            author_ = ' '.join(author_)
            author_l = author_.split("-",1)
            authors = author_l[0].split(",")
            authors = [author.strip() for author in authors]
            publisher = author_l[1].split("-")[-1].strip()
            date = re.findall(r'\d+', author_l[1])[0]
            number_citation = link.xpath(".//div[@class='gs_fl gs_flb']/a[3]/text()").get()
            number_citation = re.findall(r'\d+', number_citation)[0]
            
            yield{
                "title" : title,
                "link" : url,
                "authors" : authors,
                "number_citation" : number_citation,
                "date" : date,
                "publisher" : publisher
            }
        
            
             