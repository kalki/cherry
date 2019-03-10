import scrapy
import logging


class SummarySpider(scrapy.Spider):
    name = "summary"

    start_urls = [
        "https://tenki.jp/sakura/"
    ]

    def parse(self, response):
        logging.info("Main page " + response.url + " parsing")
        count = 0

        for area_link in response.css("div.top-map-sakura-wrap>dl[class^='area']>dd"):
            area_name = area_link.css("a>span::text").extract_first()
            url = area_link.css("a::attr(href)").extract_first()
            if url is not None:
                url = response.urljoin(url)
                logging.info(area_name + ", yield " + url)
                req = scrapy.Request(url, callback=self.parse_site)
                req.meta["area_name"] = area_name
                count = count + 1
                yield req
        logging.info("Main page yield " + str(count) + " areas")

    def parse_site(self, response):
        area_name = response.meta["area_name"]
        count = 0
        logging.info(area_name + " page " + response.url + " parsing")

        region_name = response.css("nav#delimiter>ol>li:nth-of-type(3)>a>span::text").extract_first()
        region_name = region_name.strip() if region_name is not None else ""

        for site in response.css("ul.sakura-entries>li"):
            site_url = site.css("a::attr(href)").extract_first()
            site_url = site_url.strip() if site_url is not None else ""
            site_img_url = site.css("a>div.img-wrap>div.img-box>img::attr(src)").extract_first()
            site_img_url = site_img_url.strip() if site_img_url is not None else ""
            site_name = site.css("a>div.text-box>p.name::text").extract_first()
            if site_name is not None:
                count = count + 1
                yield {
                    "aname": area_name,
                    "sname": site_name,
                    "rname": region_name,
                    "site_url": site_url,
                    "image_url": site_img_url
                }
        logging.info(area_name + " page yield " + str(count) + " sites")

        is_next = False
        for page in response.css("ul.pager-entries>li"):
            current = page.css("span::text").extract_first()
            if current is not None and current.strip() != "<<" and current.strip() != ">>":
                logging.info(area_name + " page index is " + current)
                is_next = True
            elif is_next:
                next_url = page.css("a::attr(href)").extract_first()
                if next_url is not None:
                    next_url = response.urljoin(next_url)
                    logging.info(area_name + " page yield " + next_url)
                    req = scrapy.Request(next_url, callback=self.parse_site)
                    req.meta["area_name"] = area_name
                    yield req
                break
