import threading, queue, requests, time, csv
from parsers import parse_page, find_page_count

def request_engine():
    global command_queue
    global proxy_rotator

    with open("valid_proxys.txt", "r") as file:
        proxies = file.read().split("\n")

        while True:
            proxy_lock.acquire() # Increment safely with thread lock
            proxy = proxies[proxy_rotator % len(proxies)]
            proxy_rotator += 1  
            proxy_lock.release()

            url = command_queue.get()

            try:
                print(f"Trying {proxy} in proxy rotator for {url}.")
                response = requests.get(url,
                                        headers=headers_args,
                                        timeout=30,
                                        proxies={"http": proxy,
                                                "https": proxy})
                
                if response.status_code == 200:
                    return response.text

            except requests.exceptions.Timeout: # This is to catch timeouts
                print("Connection Timeout")
                command_queue.put(url)  
                continue

            except: # This is to catch all failed responce codes that are not "200"
                command_queue.put(url)
                continue
                

def first_page(): # Scrapping the first page seperatly to find out how many pages of books there are.
    global page_count

    while not command_queue.empty():
        response_str = request_engine()
        print("First page succress")
        page_count = find_page_count(response_str)
        with open("scrapped_books.csv", mode="a") as file:
            csv_instansiation = csv.writer(
                file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_instansiation.writerow(
                ["Book Name", "Price", "Book Rating", "Book Link"])
            for i in parse_page(response_str):
                csv_instansiation.writerow(i)


def all_found_pages():

    while not command_queue.empty():
        response_str = request_engine()
        with open("scrapped_books.csv", mode="a") as file:
            csv_instansiation = csv.writer(
                file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for i in parse_page(response_str):
                csv_instansiation.writerow(i)

        if command_queue.qsize() > 0:
            print(f"{command_queue.qsize()} of {command_list_size} remaining.")
            

if __name__ == "__main__":
    command_queue = queue.Queue()
    proxy_rotator = 0
    proxy_lock = threading.Lock()
    headers_args = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding": "gzip, deflate",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    first_page_link = "https://books.toscrape.com"
    page_count = -1

    command_queue.put(first_page_link)
    single_thread = threading.Thread(target=first_page)
    single_thread.start()

    single_thread.join()

    url_list = []
    for num in range(2, page_count + 1):
        url_list.append(
            f"https://books.toscrape.com/catalogue/page-{num}.html")

    command_list_size = len(url_list)
    for url in url_list:
        command_queue.put(url)

    threads = []
    for _ in range(12):
        thread = threading.Thread(target=all_found_pages)
        thread.start()
        threads.append(thread)

    thread.join()

    print("Await Completion")