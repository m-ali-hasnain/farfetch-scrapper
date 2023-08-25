import time

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
from ..items import FarfetchScrapperItem

# Constants
WEBSITE_NAME = "farfetch"
FIT_KEYWORDS = ["Maternity", "Petite", "Plus Size", "Curvy", "Tall", "Mid-weight", "High-waisted", "Oversized"]

NECK_LINE_KEYWORDS = ["Scoop", "Round Neck," "U Neck", "U-Neck", "V Neck",
                      "V-neck", "V Shape", "V-Shape", "Deep", "Plunge", "Square",
                      "Straight", "Sweetheart", "Princess", "Dipped", "Surplice",
                      "Halter", "Asymetric", "One-Shoulder", "One Shoulder",
                      "Turtle", "Boat", "Off- Shoulder", "Collared", "Cowl", "Neckline"]

OCCASIONS_KEYWORDS = ["office", "work", "smart", "workwear", "wedding", "nuptials",
                      "night out", "evening", "spring", "summer", "day", "weekend",
                      "outdoor", "outdoors", "adventure", "black tie", "gown",
                      "formal", "cocktail", "date night", "vacation", "vacay", "fit",
                      "fitness", "athletics", "athleisure", "work out", "sweat",
                      "swim", "swimwear", "lounge", "loungewear", "beach"]

LENGTH_KEYWORDS = ["mini", "short", "maxi", "crop", "cropped", "sleeves",
                   "tank", "top", "three quarter", "ankle", "long"]

STYLE_KEYWORDS = ["bohemian", "embellished", "sequin", "floral", "off shoulder",
                  "puff sleeve", "bodysuit", "shell", "crop", "corset", "tunic",
                  "bra", "camisole", "polo", "aviator", "shearling", "sherpa",
                  "biker", "bomber", "harrington", "denim", "jean", "leather",
                  "military", "quilted", "rain", "tuxedo", "windbreaker", "utility",
                  "duster", "faux fur", "overcoat", "parkas", "peacoat", "puffer",
                  "skater", "trench", "Fleece", "a line", "bodycon", "fitted",
                  "high waist", "high-low", "pencil", "pleat", "slip", "tulle",
                  "wrap", "cargo", "chino", "skort", "cigarette", "culottes",
                  "flare", "harem", "relaxed", "skinny", "slim", "straight leg",
                  "tapered", "wide leg", "palazzo", "stirrup", "bootcut", "boyfriend",
                  "loose", "mom", "jeggings", "backless", "bandage", "bandeau",
                  "bardot", "one-shoulder", "slinger", "shift", "t-shirt", "smock",
                  "sweater", "gown"]

AESTHETIC_KEYWORDS = ["E-girl", "VSCO girl", "Soft Girl", "Grunge", "CottageCore",
                      "Normcore", "Light Academia", "Dark Academia ", "Art Collective",
                      "Baddie", "WFH", "Black", "fishnet", "leather"]
LINKS_KEYWORDS = ["dress", "knitwear", "jacket", "top", "pant", "lingerie",
                  "jumpsuit", "beachwear", "shirt", "activewear", "denim", "coat", "sweatshirt", "clothes", "innerwear",
                  "wear", "loungewear", "tees", "bottoms", "outwear", ""]

FABRICS_KEYWORDS = ["polyester", "cashmere", "viscose", "Machine wash cold", "metallic", "silk", "rayon", "spandex",
                    "TENCEL", "cotton", "elastane", "lyocell", "LENZING", "LYCRA", "%"]
DISALLOWED_CATEGORIES = ["shoes", "joggers", "heels", "accessories", "cape", "socks"]
CATEGORY_KEYWORDS = ['Bottom', 'Shift', 'Swim Brief', 'Quilted', 'Boyfriend',
                     'Padded', 'Track', 'Other', 'Oversized', 'Denim Skirt',
                     'Stick On Bra', 'Cardigan', 'Thong', 'Romper', 'Pea Coat',
                     'Skater', 'Swing', 'Lingerie & Sleepwear', 'Wrap', 'Cargo Pant',
                     'Cape', 'Trucker', 'Nursing', 'Bikini', 'Parka', 'Regular', 'Denim',
                     'Duster', 'Faux Fur', 'Hoodie', 'Bralet', 'Overcoat', 'Corset Top',
                     'T-Shirt', 'Mini', 'Maxi', 'Blazer', 'Super Skinny', 'Summer Dresses',
                     'Chino', 'Short', 'Set', 'Military', 'Overall', 'Vest', 'Bomber Jacket',
                     'Tea', 'Ski Suit', 'Work Dresses', 'High Waisted', 'Culotte', 'Overall Dress',
                     'Jean', 'Loungewear', 'Leather Jacket', 'Unpadded', 'Coats & Jackets', 'Underwired',
                     'Corset', 'Night gown', 'Poncho', 'Pant', 'Cigarette', 'Sweatpant', 'Rain Jacket',
                     'Loose', 'Swimwear & Beachwear', 'Shirt', 'Denim Jacket', 'Co-ord', 'Tight', 'Vacation Dress',
                     'Harrington', 'Bandage', 'Bootcut', 'Biker', 'Crop Top', 'Trench', 'Tracksuit', 'Suit Pant',
                     'Relaxed', 'Day Dresses', 'Tuxedo', 'Tapered', 'Wide Leg', 'Bohemian', 'Pleated', 'Wiggle',
                     'One Shoulder', 'Smock Dress', 'Flare', 'Peg Leg', 'Cover Up', 'Unitard', 'Sweater',
                     'Lounge', 'Top', 'Bodycon', 'Push Up', 'Slip', 'Knitwear', 'Leather', 'Pencil Dress',
                     'Off Shoulder', 'Jersey Short', 'Multiway', 'Balconette', 'Wax Jacket', 'Coat', 'Brief',
                     'Coach', 'Jumpsuits & Rompers', 'Bra', 'Long Sleeve', 'Fleece', 'Activewear', 'Jegging',
                     'Outerwear', 'Bandeau', 'Slim', 'Going Out Dresses', 'Bardot', 'Pajama', 'Sweatsuit',
                     'Blouse', 'Sweaters & Cardigans', 'Straight Leg', 'Windbreaker', 'Tank Top', 'Cold Shoulder',
                     'Halter', 'Dresses', 'T-Shirt', 'Trouser', 'Cami', 'Camis', 'Wedding Guest', 'Bodysuit', 'Triangle',
                     'Casual Dresses', 'Chino Short', 'Boiler Suit', 'Raincoat', 'Formal Dresses', 'Skinny',
                     'Jumper', 'Strapless', 'Cropped', 'Jacket', 'Bridesmaids Dress', 'Tunic', 'A Line',
                     'Denim Dress', 'Cocktail', 'Skirt', 'Jumpsuit', 'Shapewear', 'Occasion Dresses',
                     'Hoodies & Sweatshirts', 'Sweatshirt', 'Aviator', 'Sweater Dress', 'Sports Short',
                     'Shirt', 'Puffer', 'Cargo Short', 'Tulle', 'Swimsuit', 'Mom Jean', 'Legging',
                     'Plunge', 'Teddie', 'Denim Short', 'Intimate', 'Pencil Skirt', 'Backless', 'Tank']

CATEGORY_TO_TYPE = {
    'Co-ords': ['Co-ord', 'Sweatsuit', 'Tracksuit', 'Set'],
    'Coats & Jackets': ['Coats & Jacket', 'Cape', 'Cardigan', 'Coat', 'Jacket', 'Poncho', 'Ski Suit', 'Vest', 'Blazer'],
    'Dresses': ['Dresses', 'Bridesmaids Dress', 'Casual Dress', 'Going Out Dress', 'Occasion Dress',
                'Summer Dress', 'Work Dress', 'Formal Dress', 'Day Dress', 'Wedding Guest', 'Vacation Dress'],
    'Hoodies & Sweatshirts': ['Hoodies & Sweatshirts', 'Fleece', 'Hoodie', 'Sweatshirt'],
    'Denim': ['Denim Jacket', 'Denim Dress', 'Denim Skirt', 'Denim Short', 'Jean', 'Jegging'],
    'Jumpsuits & Rompers': ['Jumpsuits & Rompers', 'Boiler Suit', 'Jumpsuit', 'Overall', 'Romper', 'Unitard'],
    'Lingerie & Sleepwear': ['Lingerie & Sleepwear', 'Intimate', 'Bra', 'Brief', 'Corset', 'Bralet', 'Night gown',
                             'Pajama', 'Shapewear', 'Slip', 'Teddie', 'Thong', 'Tight', 'Bodysuit', 'Camis', 'Cami'],
    'Loungewear': ['Loungewear', 'Lounge', 'Activewear', 'Outerwear', 'Hoodie', 'Legging', 'Overall', 'Pajama',
                   'Sweatpant', 'Sweatshirt', 'Tracksuit', 'T-Shirt'],
    'Bottoms': ['Bottom', 'Chino', 'Legging', 'Pant', 'Suit Pant', 'Sweatpant', 'Tracksuit', 'Short', 'Skirt',
                'Trouser'],
    'Sweaters & Cardigans': ['Sweaters & Cardigans', 'Sweatpant', 'Cardigan', 'Sweater', 'Knitwear'],
    'Swimwear & Beachwear': ['Swimwear & Beachwear', 'Bikini', 'Cover Up', 'Short', 'Skirt', 'Swim Brief', 'Swimsuit'],
    'Tops': ['Top', 'Blouse', 'Bodysuit', 'Bralet', 'Camis', 'Corset Top', 'Crop Top', 'Shirt', 'Sweater',
             'Tank Top', 'T-Shirt', 'Tunic'],
}
CATEGORY_TO_STYLE = {
  'Co-ords' : ['Co-ords'],
  'Coats & Jackets' : ['Coats & Jackets', 'Aviator', 'Biker', 'Bomber Jacket', 'Coach', 'Denim Jacket', 'Duster', 'Faux Fur', 'Harrington', 'Leather', 'Leather Jacket', 'Military', 'Other', 'Overcoat', 'Parkas', 'Pea Coat', 'Puffer', 'Quilted', 'Raincoats', 'Rain Jackets', 'Regular', 'Skater', 'Track', 'Trench', 'Trucker', 'Tuxedo', 'Wax Jacket', 'Windbreaker'],
  'Dresses' : ['Dresses', 'A Line', 'Backless', 'Bandage', 'Bandeau', 'Bardot', 'Bodycon', 'Bohemian', 'Cold Shoulder', 'Denim', 'Jumper', 'Leather', 'Long Sleeve', 'Off Shoulder', 'One Shoulder', 'Other', 'Overall Dress', 'Pencil Dress', 'Shift', 'Shirt', 'Skater', 'Slip', 'Smock Dresses', 'Sweater Dress', 'Swing', 'Tea', 'T-Shirt', 'Wiggle', 'Wrap', 'Cocktail', 'Maxi', 'Mini'],
  'Hoodies & Sweatshirts' : ['Hoodies & Sweatshirts'],
  'Denim' : ['Jeans', 'Bootcut', 'Boyfriend', 'Cropped', 'Flare', 'High Waisted', 'Loose', 'Mom Jeans', 'Other', 'Regular', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg'],
  'Jumpsuits & Rompers' : ['Jumpsuits & Rompers'],
  'Lingerie & Sleepwear' : ['Lingerie & Sleepwear', 'Balconette', 'Halter', 'Multiway', 'Nursing', 'Padded', 'Plunge', 'Push Up', 'Stick On Bra', 'Strapless', 'Triangle', 'T-Shirt', 'Underwired', 'Unpadded'],
  'Loungewear' : ['Loungewear'],
  'Bottoms' : ['Bottoms', 'Cargo Pants', 'Cigarette', 'Cropped', 'Culottes', 'Flare', 'High Waisted', 'Other', 'Oversized', 'Peg Leg', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg', 'Cargo Shorts', 'Chino Shorts', 'Denim', 'High Waisted', 'Jersey Shorts', 'Other', 'Oversized', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Sports Shorts', 'A Line', 'Bodycon', 'Denim', 'High Waisted', 'Other', 'Pencil Skirt', 'Pleated', 'Skater', 'Slip', 'Tulle', 'Wrap'],
  'Sweaters & Cardigans' : ['Sweaters & Cardigans'],
  'Swimwear & Beachwear' : ['Swimwear & Beachwear', 'Halter', 'High Waisted', 'Multiway', 'Padded', 'Plunge', 'Strapless', 'Triangle', 'Underwired'],
  'Tops' : ['Tops'],
}

base_url = "http://www.farfetch.com/"


class FarfetchSpider(scrapy.Spider):
    name = 'farfetch'
    allowed_domains = ['www.farfetch.com']

    def __init__(self, *a, **kw):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1920,1080");
        options.add_argument("--start-maximized");
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        super().__init__(*a, **kw)


    def start_requests(self):
        url = "https://www.farfetch.com/pk/shopping/women/clothing-1/items.aspx"
        yield scrapy.Request(url=url, callback=self.parse_pages)


    def parse_pages(self, response):
        for i in range(1, 200):
            url = f"{response.url}?page={i}&view=90&sort=3"
            yield scrapy.Request(url=url, callback=self.parse_products_links)

    def parse_products_links(self, response):
        products_links = response.css("div.ltr-1g1ywla.elu6vcm1 div ul div a::attr('href')").getall()
        for link in products_links:
            url = f"{base_url}{link}"
            print("URL IS:" + str(url))
            yield scrapy.Request(url=url, callback=self.parse_product)

    def parse_product(self, response):
        url = response.request.url
        external_id = response.css("._3687c0::text").get()
        name = response.css("._6b7f2f>._b4693b::text").get()
        price = response.xpath('//span[@data-tstid = "priceInfo-original" ] /text()').get()
        if price:
            price = price.strip()


        details = response.xpath('//div[@data-tstid="productDetails"] /div[1] //text()').getall()
        details = [det for det in details if not re.search("Made In", det) and not det.startswith(" ")]
        fit_meta = response.xpath('//h4[contains(text(), "Fitting information")] /parent::* //text()').getall()
        details_meta = details+fit_meta

        top_best_seller = ""
        colors = response.css("ul._ef6f60 li:nth-child(1)::text").get()
        if colors:
            colors = colors.split("/")
            colors = [color.strip() for color in colors]
        else:
            colors = []

        number_of_reviews = ''
        fabrics = response.xpath("//h4[contains(text(), 'Composition')] /parent::* /p /text()").get()
        categories = []
        scrapped_categories = remove_duplicates(find_categories(name, response.request.url))
        extracted_categories = extract_categories_from(url)
        if extracted_categories:
            categories = find_actual_parent(scrapped_categories, extracted_categories)
        else:
            extracted_categories = extract_categories_from(name)
            if extracted_categories:
                categories = find_actual_parent(scrapped_categories, extracted_categories)
            else:
                extracted_categories = extract_categories_from(scrapped_categories)
                if extracted_categories:
                    categories = find_actual_parent(scrapped_categories, extracted_categories)

        fit = ' '.join(find_keywords_from_str(details, name, url,  FIT_KEYWORDS)).strip()
        neck_line = ' '.join(find_keywords_from_str(details,name, url, NECK_LINE_KEYWORDS)).strip()
        length = ' '.join(find_keywords_from_str(details, name, url, LENGTH_KEYWORDS)).strip()
        occasions = find_keywords_from_str(details, name, url,  OCCASIONS_KEYWORDS)
        style = find_keywords_from_str(details, name, url, STYLE_KEYWORDS)
        gender = "women"
        sizes = response.xpath('(//select[@id="dropdown"])[1] /option /text()').getall()[1:]
        sizes = [re.sub("\s?-\s?\$\d+", "",size).strip() for size in sizes]
        sizes = [re.sub("\s?-\s?Last 1 left", "", size).strip() for size in sizes]
        self.driver.get(response.request.url)
        self.driver.implicitly_wait(5)
        images = self.driver.find_elements(By.CSS_SELECTOR, "div.e12qj49u0 img")
        images = [image.get_attribute('src') for image in images]

        item = FarfetchScrapperItem()
        item["external_id"] = external_id
        item["url"] = response.url
        item["name"] = name
        item["categories"] = categories
        item["price"] = price
        item["colors"] = colors
        item["sizes"] = sizes
        item["fabric"] = fabrics
        item["fit"] = fit
        item["details"] = details
        item["images"] = images
        item["number_of_reviews"] = number_of_reviews
        item["review_description"] = []
        item["top_best_seller"] = top_best_seller
        item["style"] = style
        item["length"] = length
        item["neck_line"] = neck_line
        item["occasions"] = occasions
        # item["aesthetics"] = aesthetics
        item["gender"] = gender
        item["meta"] = {}
        item["website_name"] = WEBSITE_NAME
        if not in_disallowed_categories(name, response.request.url) and categories:
            yield item

# Helpers

def find_categories(name, url):
    categories = []
    for keyword in CATEGORY_KEYWORDS:
        if re.search(keyword, name, re.IGNORECASE) or re.search(keyword, url, re.IGNORECASE):
            categories.append(keyword)

    return list(set(categories))

# This helper finds fabric from details and returns it
def find_fabric_from_details(details):
    product_details = ' '.join(details)
    fabrics_founded = re.findall(r"""(\d+ ?%\s?)?(
         velvet\b|silk\b|satin\b|cotton\b|lace\b|
         sheer\b|organza\b|chiffon\b|spandex\b|polyester\b|
         poly\b|linen\b|nylon\b|viscose\b|Georgette\b|Ponte\b|
         smock\b|smocked\b|shirred\b|Rayon\b|Bamboo\b|Knit\b|Crepe\b|
         Leather\b|polyamide\b|Acrylic\b|Elastane\bTencel\bCashmere\b|Polyurethane\b|Rubber\b|Lyocell\b)\)?""",
                                 product_details,
                                 flags=re.IGNORECASE | re.MULTILINE)
    fabric_tuples_joined = [''.join(tups) for tups in fabrics_founded]
    # Removing duplicates now if any
    fabrics_final = []
    for fabric in fabric_tuples_joined:
        if fabric not in fabrics_final:
            fabrics_final.append(fabric)

    return ' '.join(fabrics_final).strip()

def in_disallowed_categories(name, url):
    for keyword in DISALLOWED_CATEGORIES:
        if re.search(keyword, name, re.IGNORECASE) or re.search(keyword, url, re.IGNORECASE):
            return True

    return False

def remove_duplicates(ls):
    return list(set(ls))

def find_keywords_from_str(details, name, url, keywords):
    finals = []
    details = ' '.join(details)
    for keyword in keywords:
        if re.search(keyword, details, re.IGNORECASE) or re.search(keyword, name, re.IGNORECASE) or \
                re.search(keyword, url, re.IGNORECASE):
            if keyword not in finals:
                finals.append(keyword)

    return finals

# This function maps category we have extracted from name or url to taxonomy,
# and then it returns the list of extracted keywords.
def map_to_parents(cats):
    # where cats -> categories
    # cat -> category
    finals = []
    for cat in cats:
        for key in CATEGORY_TO_TYPE:
            if re.search(cat, ' '.join(CATEGORY_TO_TYPE[key]), re.IGNORECASE):
                finals.append(key)
    if not finals:
        for cat in cats:
            for key in CATEGORY_TO_STYLE:
                if re.search(cat, ' '.join(CATEGORY_TO_STYLE[key]), re.IGNORECASE):
                    finals.append(key)

    return list(set(finals))


# This function find real parent category from the list of extracted categories we provided
# Arguments: -> here first arg is scrapped categories and second is one which is list of extracted keywords
# we basically loop over scrapped categories and check if any category from scrapped one lies in extracted ones
def find_actual_parent(scrapped_cats, categories):
    finals = []
    final_categories = map_to_parents(categories)
    if len(final_categories) > 1:
        for fc in final_categories:
            if re.search(fc, ' '.join(scrapped_cats), re.IGNORECASE):
                finals.append(fc)

        if finals:
            return finals
        else:
            return []
    else:
        if final_categories:
            return final_categories
        else:
            return []


# This function extracts category keywords from product attribute passed as an argument to it
def extract_categories_from(keyword):
    cats = []  # categories
    if type(keyword) == list:
        keyword = ' '.join(keyword)

    for cat in CATEGORY_KEYWORDS:
        if re.search(cat, keyword, re.IGNORECASE):
            cats.append(cat)

    return cats
