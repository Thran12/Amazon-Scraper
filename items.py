# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonscraperItem(scrapy.Item):
    # define the fields for your item here like:
    Asin_Number=scrapy.Field()
    product_title = scrapy.Field()
    price_fraction=scrapy.Field()
    ratings_star=scrapy.Field()
    dimension=scrapy.Field()
    weight=scrapy.Field()
    brand_name=scrapy.Field()

class BookScraperItem(scrapy.Item):
    book_asin=scrapy.Field()
    book_author=scrapy.Field()
    book_title = scrapy.Field()
    kindle_price=scrapy.Field()
    book_weight=scrapy.Field()
    book_dimension=scrapy.Field()
    book_rating=scrapy.Field()