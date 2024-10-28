from bs4 import BeautifulSoup
import re

def find_page_count(markup):
    soup = BeautifulSoup(markup, "lxml")
    page_num = soup.find("li", class_="current")
    match = re.findall("[0-9]+", page_num.string)
    return int(max(match))

def parse_page(markup):
    page_records = []
    
    soup = BeautifulSoup(markup, "lxml")
    for item in soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3"):
        record = []
        # Book name, Price, Rating, Book link

        img_tag = item.find("img")
        record.append(img_tag["alt"])  # Book name

        price_tag = item.find("p", class_="price_color")
        book_price = price_tag.string
        new_book_price = book_price.replace("Â","")
        record.append(new_book_price) # Book price

        for rating in ratings_lookup.keys():
            if item.find("p", class_=rating) is not None:
                found_rating = item.find("p", class_=rating)
                class_string = " ".join(found_rating['class']) 
                record.append(f"{ratings_lookup[class_string]} star(s)")
        page_records.append(record) # Rating

        anchor_tag = item.find("a")
        link = f'https://books.toscrape.com/catalogue/{anchor_tag["href"]}' 
        link = link.replace("catalogue/catalogue/", "catalogue/") # Rough patch to fix a double catalogue string
        record.append(link) # Book link
        
    return page_records

ratings_lookup = {
    "star-rating One": 1,
    "star-rating Two": 2,
    "star-rating Three": 3,
    "star-rating Four": 4,
    "star-rating Five": 5
}