#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import urllib2
from bs4 import BeautifulSoup
import transmissionrpc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Search for ThePirateBay.")
    parser.add_argument("-k", "--keyword", metavar="KEYWORD", type=str, help="Keyword")
    parser.add_argument("-a", "--author", metavar="AUTHOR", type=str, nargs='+', help="Authors")
    parser.add_argument("-d", "--depth", metavar="DEPTH", default="10", type=int,
                        help="The number of pages to be searched (default 10)")
    args = parser.parse_args()

    tc= transmissionrpc.Client('localhost', port=8091, user='transmission', password='0missions')

    torrents = []
    for i in range(args.depth):
        url = "http://thepiratebay.sx/search/%s/%d/99/0" % (args.keyword, i)
        failTime = 0
        while True:
            if failTime >= 10:
                print "fetching " + url + " failed"
                break
            try:
                print "fetching " + str(failTime) + " " + url
                soup = BeautifulSoup(urllib2.urlopen(url, timeout=15))
                rows = soup.find('table', id='searchResult').findAll('tr')[1:-1]
            except AttributeError, e:
                print "    wrong page fetched."
                failTime += 1
            except urllib2.URLError, e:
                print "    timeout."
                failTime += 1
            else:
                break

        if failTime >= 10:
            continue

        for row in rows:
            title = row.div.a.text
            magnet = row.find("a", title="Download this torrent using magnet")
            try:
                author = row.font.a.text
            except AttributeError, e:
                author = "Anonymous"
            if author in args.author:
                torrents.append({
                    "title": title,
                    "magnet": magnet.attrs["href"],
                    "author": author})
                #end for i in range(args.depth)

    for torrent in torrents:
        print torrent["title"]
        print "    author: " + torrent["author"]
        print "    " + torrent["magnet"]
        tc.add_torrent(torrent["magnet"])