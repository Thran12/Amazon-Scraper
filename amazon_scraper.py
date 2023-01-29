from numpy import NaN
import  scrapy
from scrapy import FormRequest
from ..items import AmazonscraperItem, BookScraperItem
import regex as re
class quote_scraper(scrapy.Spider):
    name='amazon'
    count_page=1
    """def __init__(self, *args, **kwargs): 
      super(quote_scraper, self).__init__(*args, **kwargs) 
      self.start_urls = [kwargs.get('start_url')]"""   
    start_urls=["https://www.amazon.com/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A3011391011&ref_=nav_em__nav_desktop_sa_intl_laptop_accessories_0_2_6_7"]
    def parse(self,response):
        def return_url(response):
                next_links=response.xpath("//span[@class='s-pagination-strip']//a/@href").extract()
                len_url=len(next_links)
                if quote_scraper.count_page==1 or quote_scraper.count_page==2:
                    quote_scraper.count_page+=1
                    url_to_request=next_links[-1]
                elif len_url>=4:
                    url_to_request=None
                else:
                    quote_scraper.count_page+=1
                    url_to_request=next_links[-1]
                return url_to_request
        get_category=response.css("span#nav-search-label-id::text")[0].extract()
        data_asin=response.css('div::attr(data-asin)').extract()
        if get_category == 'Books':
            for data_ in data_asin:
                if data_ is not '':
                    urls=f'https://www.amazon.com/dp/{data_}'
                    yield response.follow(urls,callback=self.extract_books)
                
                # here the below help extracting data in tech related websites

        else:
            for data_ in data_asin:
                if data_ is not '':
                    urls=f'https://www.amazon.com/dp/{data_}'
                    yield response.follow(urls,callback=self.extract_tech)

        
                    #yield scrapy.Request(urls,callback=self.extract_page)
            # to move to the next page we need to build a function here

            #next_links=response.xpath("//span[@class='s-pagination-strip']//a/@href").extract()
            #len_url=len(next_links)
            
            '''if quote_scraper.count_page==1 or quote_scraper.count_page==2:
                    quote_scraper.count_page+=1
                    url_to_request=next_links[-1]
            elif len_url>=4:
                    url_to_request=None
            else:
                    quote_scraper.count_page+=1
                    url_to_request=next_links[-1]

            #get_url=return_url(response)
            #print(get_url)'''
            url_to_request=return_url(response)
            if url_to_request is not None:
                yield response.follow(url_to_request,callback=self.parse)


    def extract_books(self,response):
        book_=BookScraperItem()
        try:
            book_author=response.xpath('//a[@data-asin=$var]/text()',var=response.xpath('//a/@data-asin').get())[0].extract()
        except IndexError or ValueError:
            book_author='Unknown Author'
        books_rating=response.xpath('//span[@class="a-icon-alt"]/text()').get()
        Books_Rate='No Ratings'if (books_rating=='Previous page of related Sponsored Products') or (books_rating=='Previous page') else books_rating
        # Books Asin
        '''try:
        book_asin=response.xpath('//a/@data-asin').get()
        except:
            book_asin=re.findall(r'/[A-Z0-9_]+',str(response.url))[0][1:]'''
        book_asin=re.findall(r'/[A-Z0-9_]+',str(response.url))[0]
        book_asin=book_asin[1:]

        #book_asin=re.findall(r'/[A-Z0-9_]+',str(response.url))[0][1:]
        book_title=response.css('span#productTitle::text')[0].extract()
        #price_book=response.xpath("//span[@class='a-size-base a-color-price a-color-price']/text()").extract()[0]
        price_book=response.xpath('//span[@class="a-color-base"]//text()').re(r'[0-9.$]+')[0]
        try:
            weight_book=''.join(response.xpath('//div[@id="detailBullets_feature_div"]//text()').re(r'([0-9. ]+)(pounds|ounces)'))
        except :
            weight_book='Weight Not Given'
        try:   
            books_dimension=response.xpath('//div[@id="detailBullets_feature_div"]//text()').re(r'[0-9.x ]+inches')[0]
        except IndexError or ValueError:
            books_dimension='Dimension not Given'
        book_['book_author']=book_author
        book_['book_rating']=Books_Rate
        book_['book_asin']=book_asin
        book_['book_title']=book_title
        book_['kindle_price']=price_book
        book_['book_weight']=weight_book
        book_['book_dimension']=books_dimension
        yield book_


    def extract_tech(self,response):
        items=AmazonscraperItem()
        #price_=response.css("span.a-offscreen").extract()
        def product_asin(response):
                    book_asin=re.findall(r'/[A-Z0-9_]+',str(response.url))[0]
                    book_asin=book_asin[1:]
                    return book_asin
        def product_titles(response):
           product_title=(response.xpath("//h1[@id='title']//span[@id='productTitle']/text()")[0].extract()).strip()
           return product_title
        def ratings_values(response):
            try:
                ratings_star=response.xpath('//span[@class="a-icon-alt"]/text()')[0].extract()
            except:
                ratings_star="No Rating Given"
            return ratings_star

        # extracting brand using helper function
        def brand_names(response):
            try:
                Brand_name=response.xpath("//a[@id='bylineInfo']/text()").get()
            except:
                Brand_name="No Brand Name"
            return Brand_name  
        
        def prices(response):
            try:
                price_0=response.xpath('//span[@class="a-offscreen"]/text()').extract()
                price_0=re.findall(r'([0-9]+)\.([0-9]+)',str(price_0))[0]
                price_='.'.join(price_0)
                price_=f'${price_}'
                if price_=='Check fit by model, Find your brand':
                    price_=response.xpath('//span[@class="a-size-base a-color-price"]//text()').get()
                    return price_
                return price_
            #except:
                ''' 
                try:
                    price_1=response.xpath("//span[@class='a-price-whole']/text()").get() 
                    price_2=response.xpath('//span[@class="a-price-fraction"]/text()').get()
                    if price_1=='00' or price_1==None or price_1=='None' or price_1==00:
                        price_1='00'
                    if price_2=='00' or price_2=='None' or price_2==None or price_2==00:
                        price_2='00'
                #price_1='00' if (price_1=='None') or (price_1==None) else price_2
                #price_2='00' if (price_2=='None') or (price_2==None) else price_2
                    price_=f'${price_1}.{price_2}'
                    if price_=='Check fit by model, Find your brand':
                        price_=response.xpath('//span[@class="a-size-base a-color-price"]//text()').get()
                        return price_
                    return price_
                    '''
                #except:
            except:
                    try:
                        price_x=list(re.findall(r'([0-9]+)\.([0-9]+)',str(response.xpath('//span[@id="style_name_0_price"]//text()').extract()))[0])
                        #price_x_=str(response.xpath('//span[@id="style_name_0_price"]//text()').extract())
                        #price_x=re.findall(r'([0-9]+)\.([0-9]+)',price_x_)[0]
                        price_x='.'.join(price_x)
                        price_=f'${price_x}'
                        return price_
                    except :
                            price_y_=list(re.findall(r'([0-9]+)\.([0-9]+)',str(response.xpath('//span[@id="size_name_0_price"]//text()').extract()))[0])
                            #price_y_=str(response.xpath('//span[@id="size_name_0_price"]//text()').extract())
                            #price_y_=re.findall(r'([0-9]+)\.([0-9]+)',price_y_)[0]
                            price_y='.'.join(price_y_)
                            price_=f'${price_y}'
                            return price_
                    finally:
                           price_='Currently UnAvailable'
                           return price_
            #finally:
             #       price_="Currently UnAvailable"
              #      return price_
            #except:
             #       price_=response.xpath('//span[@class="a-offscreen"]/text()').get()
            '''except:
                    try:
                        price_=response.xpath('//span[@id="style_name_0_price"]/text()').get()
                    except:
                        price_='Currently UnAvailable'
                        '''
                


        def pricing(response):
            #brand_name=response.xpath('//span[@id="bylineInfo"]/text()')[0].extract()
            #price_=response.xpath("//span[@class='a-offscreen']/text()").get()   
            price_1=response.xpath("//*[@id='corePriceDisplay_desktop_feature_div']/div[1]/span/span[2]/span[2]/text()").get() 
            price_2=response.xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]/span[2]/span[3]/text()').get()
            price_=f'${price_1}.{price_2}'
            
            try:
                if price_!='$None.None':
                    price__=re.split(r'.None',price_)[0]
                    price_=price__
                elif price_=='$None.None' or price_==None:
                    try:
                        price_=response.css('span.offscreen::text').get()
                    except ValueError:
                        price_=response.xpath('//span[@class="a-offscreen"]/text()').get()
            except:
                    try:
                        price_=response.xpath('//span[@id="style_name_0_price"]/text()').get()
                    except ValueError:
                        price_='currently unavailable'
            return price_
        
        def product_details(response,value_):
            product_details=response.xpath('//*[@id="prodDetails"]').extract()
            # some pages have product details in the form of of detailBullets_feature_div we need some new logic So also working on that
            if value_=='Dimension':
                try:
                    product_details_dimension=re.findall(r'[0-9.x ]+inches ',str(product_details))[0]
                except:
                    product_details_dimension="No dimension"
                return product_details_dimension
            elif value_=='Weights':
                try: 
                    product_weight=''.join(re.findall(r'([0-9. ]+)(pounds|ounces)',str(product_details))[0])
                except:
                    product_weight="No weight"
                return product_weight


        brand_name=brand_names(response)
        price_=prices(response)
        ratings_star=ratings_values(response)
        asin_=product_asin(response)
        product_details_dimension=product_details(response,'Dimension')
        product_weight=product_details(response,'Weights')
        product_title=product_titles(response)
        #items={'product_title':product_title,'price-fraction':price_,'ratings_star':ratings_star}

        items['Asin_Number']=asin_
        items['product_title']=product_title
        items['price_fraction']=price_
        items['ratings_star']=ratings_star
        items['dimension']=product_details_dimension
        items['weight']=product_weight
        items['brand_name']=brand_name
        yield items


        def extracting_home_kitchen(responses):
            #check variation style name.
            #if variation then variation prices in dictionary if not general price
            def asin():
                    product_asin=re.findall(r'/[A-Z0-9_]+',str(response.url))[0]
                    product_asin=product_asin[1:]
                    return product_asin
            def title():
                title_=(response.xpath('//span[@id="productTitle"]/text()').extract()).strip()
                return title_
            def price_value():
                #  i think so we need to open the data in the lnks
                price_value=response.xpath('//span[@class="a-offscreen"]//text()').extract_first()
                return price_value
            def ratings():
                ratings_=response.xpath('//span[@class="a-icon-alt"]//text()').extract_first()
                return ratings_
            def product_details(response,value_):
                product_details=response.xpath('//*[@id="prodDetails"]').extract()
                if value_=='Dimension':
                    try:
                        product_details_dimension=re.findall(r'[0-9.x ]+inches ',str(product_details))[0]
                    except:
                        product_details_dimension="No dimension"
                    return product_details_dimension
                elif value_=='Weights':
                    try: 
                        product_weight=''.join(re.findall(r'([0-9. ]+)(pounds|ounces)',str(product_details))[0])
                    except:
                        product_weight="No weight"
                    return product_weight
            def brand_name():
                pass