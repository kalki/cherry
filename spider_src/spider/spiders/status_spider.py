import scrapy
import logging


class StatusSpider(scrapy.Spider):
    name = "status"

    start_urls = [
        "https://tenki.jp/sakura/"
    ]

    def parse(self, response):
        logging.info("Main page " + response.url + " parsing")
        count = 0

        for area_link in response.css("div.top-map-sakura-wrap>dl[class^='area']>dd"):
            url = area_link.css("a::attr(href)").extract_first()
            if url is not None:
                url = response.urljoin(url)
                req = scrapy.Request(url, callback=self.parse_site)
                count = count + 1
                yield req
        logging.info("Main page yield " + str(count) + " areas")

    def parse_site(self, response):

        count = 0
        logging.info(response.url + " parsing")

        for site in response.css("ul.sakura-entries>li"):
            site_url = site.css("a::attr(href)").extract_first()
            if site_url is not None:
                site_url = site_url.strip() if site_url is not None else ""
                site_status = site.css("a>div.text-box>p.name>span.rank-image-telop>span.rank-telop::text").extract_first()
                site_status = site_status.strip() if site_status is not None else ""
                count = count + 1
                yield {
                    "site_url": site_url,
                    "status": site_status
                }
        logging.info(response.url + " yield " + str(count) + " sites")

        is_next = False

        for page in response.css("ul.pager-entries>li"):
            current = page.css("span::text").extract_first()
            if current is not None and current.strip() != "<<" and current.strip() != ">>":
                logging.info(response.url + " index is " + current)
                is_next = True
            elif is_next:
                next_url = page.css("a::attr(href)").extract_first()
                if next_url is not None:
                    next_url = response.urljoin(next_url)
                    logging.info(response.url + " yield " + next_url)
                    req = scrapy.Request(next_url, callback=self.parse_site)
                    yield req
                break

