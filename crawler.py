import logging
import re
from urllib.parse import urlparse
from corpus import Corpus

import ssl
import urllib.request
import lxml.html

logger = logging.getLogger(__name__)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier):
        self.frontier = frontier
        self.corpus = Corpus()

        # Added for Analytics
        self.downloaded = []
        self.trap = {"Redirect" : [], "Page-Fragment" : [], "Long-URL" : []}
        self.trap_count = 0

        self.most_out_url = ""
        self.highest_out = 0

        self.subdomains = {}
        

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            self.downloaded.append(url)
            url_data = self.fetch_url(url)

            for next_link in self.extract_next_links(url_data):
                if self.corpus.get_file_name(next_link) is not None:
                    if self.is_valid(next_link):
                        self.frontier.add_url(next_link)

        # Write Analytics File
        self.write_file()

    def fetch_url(self, url):
        """
        This method, using the given url, should find the corresponding file in the corpus and return a dictionary
        containing the url, content of the file in binary format and the content size in bytes
        :param url: the url to be fetched
        :return: a dictionary containing the url, content and the size of the content. If the url does not
        exist in the corpus, a dictionary with content set to None and size set to 0 can be returned.
        """

        url_data = {
            "url": url,
            "content": None,
            "size": 0
        }
        
        # Check if URL is in corpus and the url is valid.
        if self.corpus.get_file_name(url) != None:
            
            # Get content as binary source from opened url. Handles case when
            # response is 404.
            context = ssl._create_unverified_context()
        
            try:
                request_data = urllib.request.urlopen(url, context=context)
            except:
                print(f"Out: 404 --- {url}")
                return url_data

            # Read data when response is 200.
            html_data = request_data.read()
                  
            url_data = {
                "url": url,
                "content": html_data,
                "size": len(str(html_data))
            }

            return url_data
        
        return url_data
    

    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """

        outputLinks = []

        if url_data["content"] != None:
            
            # lxml.html.make_links_absolute() returns html with all the links converted to absolute.
            aboslute_html = lxml.html.make_links_absolute(url_data["content"], url_data["url"])
        
            # Iterate over the html content. lxml.html.iterlinks returns a generator of links
            # that contain the tag and link itself. If the tag is "href" (@159), append it the link list.
            for link in lxml.html.iterlinks(aboslute_html):
                
                if link[1] == "href" and self.is_valid(link[2]):
                    print(f"In Frontier: {link[2]}")
                    outputLinks.append(link[2])
                    self.frontier.add_url(link[2])

                    # Adds subdomain to the dict if not already in it and increases the count.
                    parsed = urlparse(link[2])
                    subdomain = parsed.hostname

                    if subdomain in self.subdomains:
                        self.subdomains[subdomain] += 1
                    else:
                        self.subdomains[subdomain] = 1

        # Checks if the num of output links is greater than the highest.
        # If higher it clears the list of urls with highest outgoing links and sets the new highest.
        # If equal it just appends to list.             
        if len(outputLinks) > self.highest_out:

            self.most_out_url = url_data["url"]
            self.highest_out = len(outputLinks)

            
        return outputLinks

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        
        # The url can be opened, is in absolute form, is not a duplicate, and had a href tag affiliated with it.
        parsed = urlparse(url)
        
        # Eliminates mailto's.
        if parsed.scheme not in set(["http", "https"]):
            print(f"Out: Scheme --- {url}")
            return False
        
        # Eliminates all external urls and non-ics subdomains.
        elif "ics.uci.edu" not in parsed.netloc:
            print(f"Out: ICS-SUB --- {url}")
            return False

        # Eliminates page redirects.
        elif "http" in parsed.params or "http" in parsed.query:
            print(f"Out: Redirect --- {url}")
            self.trap["Redirect"].append(url)
            self.trap_count += 1
            return False

        # Eliminates page selectors
        elif len(parsed.fragment) > 0:
            print(f"Out: Fragment --- {url}")
            self.trap["Page-Fragment"].append(url)
            self.trap_count += 1
            return False
        
        # Eliminates pages with queries containing 6 or more consecutive digits. Most non-trap queries like ids (2 - 4 digits)
        # class numbers (3 digits), and years (4 digits) are less than 6.
        elif re.search("\d{6}", parsed.query):
            print(f"Out: Query --- {url}")
            self.trap["Long-URL"].append(url)
            self.trap_count += 1
            return False

        else:
            try:

                # Eliminates individual files.
                if not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                        + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                        + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                        + "|thmx|mso|arff|rtf|jar|csv" \
                                        + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower()):
                    print(f"In: {url}")
                    return True
                else:
                    print(f"Out: File --- {url}")
                    return False
                

            except TypeError:
                print("TypeError for ", parsed)
                return False

            
    def write_file(self):

        file  = open("analytics.txt", 'w')
        file.write("################ SUBDOMAIN : COUNT ################\n")
        for key in self.subdomains:
            file.write("{} : {}\n".format(key,self.subdomains[key]))
            

        file.write("\n################ MOST OUTGOING LINKS ##############\n")
        file.write("Most valid out links: {}\n".format(self.most_out_url))
        file.write("Count : {}\n".format(self.highest_out))

        
        file.write("\n################ DOWNLOADED URLS ###########\n")
        file.write(f"Count : {len(self.downloaded)}\n")
        for link in self.downloaded:
            file.write(f"{link}\n")

        file.write("\n################ TRAPS ###########\n")
        file.write(f"Count : {self.trap_count}\n")
        for k in self.trap.keys():
            for val in self.trap[k]:
                file.write(f"{k} : {val}\n")
            
        file.close()
