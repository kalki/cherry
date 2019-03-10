import scrapy
import logging
import re


class DetailSpider(scrapy.Spider):
    name = "detail"

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

        for site in response.css("ul.sakura-entries>li"):
            site_url = site.css("a::attr(href)").extract_first()
            if site_url is not None:
                site_req_url = response.urljoin(site_url)
                req = scrapy.Request(site_req_url, callback=self.parse_detail)
                req.meta["site_url"] = site_url.strip()
                count = count + 1
                yield req
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

    def parse_detail(self, response):
        site_url = response.meta["site_url"]
        exp = response.css("td.bloom-expectation>dl>dd::text").extract_first()
        exp = exp.strip() if exp is not None else ""
        desc = response.css("dd.sakura_point_feature::text").extract_first()
        desc = desc.strip() if desc is not None else ""
        night = ""
        event = ""
        lat = ""
        lon = ""
        addr = ""
        whour = ""

        for info in response.css("table.map-sakura-detail-status-table td.kind-status dl"):
            tag = info.css("dt::text").extract_first()
            tag = tag.strip() if tag is not None else ""
            if tag == "夜間鑑賞" and len(info.css("dd span")) == 0:
                night = info.css("dd::text").extract_first()
                night = night.strip() if night is not None else ""
            if tag == "イベント" and len(info.css("dd span")) == 0:
                event = info.css("dd::text").extract_first()
                event = event.strip() if event is not None else ""

        pattern = re.compile("center[ \t]*:[ \t]*\[([0123456789.]*)[ \t]*,[ \t]*([0123456789.]*)[ \t]*\]")
        matches = pattern.search(str(response.body))

        if matches is not None:
            lat = matches.group(1)
            lon = matches.group(2)   

        for info in response.css("div#sakura-point-access-feature table.sakura-point-info-table tr"):
            tag = info.css("th::text").extract_first()
            tag = tag.strip() if tag is not None else ""
            if tag == "住所":
                addr = info.css("td::text").extract_first()
                addr = addr.strip() if addr is not None else ""
            if tag == "平日営業時間":
                whour = info.css("td::text").extract_first()
                whour = whour.strip() if whour is not None else ""

        yield {
            "site_url": site_url,
            "exp": exp,
            "desc": desc,
            "night": night,
            "event": event,
            "lat": lat,
            "lon": lon,
            "addr": addr,
            "whour": whour
        }
