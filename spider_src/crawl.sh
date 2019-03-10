#!/bin/sh

CURRENT_DATE=`date +%Y-%m-%d`
OUTPUT_FILE=/var/www/cherry/data/$CURRENT_DATE.csv
LOG_FILE=/var/www/cherry/logs/spider_$CURRENT_DATE.log

rm -f $OUTPUT_FILE
scrapy runspider /var/www/cherry/job/spider/spider/spiders/status_spider.py -o $OUTPUT_FILE --loglevel INFO --logfile $LOG_FILE -s DOWNLOAD_DELAY=0.3
