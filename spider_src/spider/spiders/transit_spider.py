import scrapy
import urllib.parse as ul


class TransitSpider(scrapy.Spider):
    name = "transit"

    start_urls = [
        "https://tenki.jp/sakura/"
    ]

    def parse(self, response):
        for area_link in response.css("div.top-map-sakura-wrap>dl[class^='area']>dd"):
            area_name = area_link.css("a>span::text").extract_first()
            url = area_link.css("a::attr(href)").extract_first()
            if url is not None:
                url = response.urljoin(url)
                req = scrapy.Request(url, callback=self.parse_site)
                req.meta["area_name"] = area_name
                yield req

    def parse_site(self, response):
        area_name = response.meta["area_name"]
        for site in response.css("ul.sakura-entries>li"):
            site_url = site.css("a::attr(href)").extract_first()
            if site_url is not None:
                site_req_url = response.urljoin(site_url)
                req = scrapy.Request(site_req_url, callback=self.parse_detail)
                req.meta["site_url"] = site_url.strip()
                req.meta["area_name"] = area_name
                yield req

        is_next = False
        for page in response.css("ul.pager-entries>li"):
            current = page.css("span::text").extract_first()
            if current is not None and current.strip() != "<<" and current.strip() != ">>":
                is_next = True
            elif is_next:
                next_url = page.css("a::attr(href)").extract_first()
                if next_url is not None:
                    next_url = response.urljoin(next_url)
                    req = scrapy.Request(next_url, callback=self.parse_site)
                    req.meta["area_name"] = area_name
                    yield req
                break

    def parse_detail(self, response):
        site_url = response.meta["site_url"]
        area_name = response.meta["area_name"]
        addr = ""
        url = "https://transit.yahoo.co.jp/search/result?flatlon=&from=%E6%9D%B1%E4%BA%AC%E9%83%BD%E5%8D%83%E4%BB%A3%E7%94%B0%E5%8C%BA%E4%B8%B8%E3%81%AE%E5%86%85%E4%B8%80%E4%B8%81%E7%9B%AE9-1&tlatlon=&to="
        url1 = "&viacode=&via=&viacode=&via=&viacode=&via=&y=2018&m=04&d=11&hh=07&m2=0&m1=3&type=1&ticket=ic&expkind=1&ws=3&s=0&al=1&shin=1&ex=1&hb=1&lb=1&sr=1"
        
        for info in response.css("div#sakura-point-access-feature table.sakura-point-info-table tr"):
            tag = info.css("th::text").extract_first()
            tag = tag.strip() if tag is not None else ""
            if tag == "住所":
                addr = info.css("td::text").extract_first()
                addr = addr.strip() if addr is not None else ""

        if addr is not None and addr != "":
            if area_name.startswith("道"):
                target = "北海道" + addr
            elif area_name == "東京":
                target = "東京都" + addr
            elif area_name == "大阪":
                target = "大阪府" + addr
            elif area_name == "京都":
                target = "京都府" + addr
            else:
                target = area_name + "県" + addr

            target = ul.quote(target)
            req = scrapy.Request(url + target + url1, callback=self.parse_transit)
            req.meta["site_url"] = site_url
            yield req

    def parse_transit(self, response):
        site_url = response.meta["site_url"]
        transit_time = response.css("div.navPriority ul#rsltlst li:nth-of-type(1) li.time span.small::text").extract_first()

        yield {
            "site_url": site_url,
            "transit_time": transit_time
        }
