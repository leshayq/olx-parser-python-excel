from bs4 import BeautifulSoup
import requests
from time import sleep

class Parse:
    #init
    def __init__(self):
        self.user_input = str(input('Enter what you want to parse.. '))
        self.url = f'https://www.olx.ua/uk/list/q-{self.user_input}/'

        #put your headers here
        self.headers = {'User-Agent': ''}

    #get request to webpage
    def get_data(self, url):
        page = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        return soup
    
    #getting all card elements
    def get_cards(self, url):
        all_cards = self.get_data(url).findAll('div', class_='css-1apmciz')

        return all_cards
    #getting the last number of page
    def get_last_page(self, url):
        page_numbers = []
        last_page = self.get_data(url).findAll('a', class_='css-1mi714g')

        for i in last_page:
            page_number = int(i.text.strip())
            page_numbers.append(page_number)

        last_page_number = max(page_numbers)
        print('Found pages: ', last_page_number)
        return int(last_page_number)
    # finding all required attributes
    def array(self):
        base_url = f'https://www.olx.ua/uk/list/q-{self.user_input}/'
        
        # loop through pages 
        for j in range(1, self.get_last_page(base_url) + 1):
            sleep(1)

            url = f'https://www.olx.ua/uk/list/q-{self.user_input}/?page={j}'

            self.get_data(url)

            #looping through cards, getting name, price, city, url, size, link
            for i in self.get_cards(url):
                name = i.find('h6', class_='css-16v5mdi er34gjf0')
                price = i.find('p', class_='css-tyui9s er34gjf0')
                city = i.find('p', class_='css-1a4brun er34gjf0')
                url = i.find('a', class_='css-z3gu2d').get('href')
                if i.find('span', class_='css-1x8agcm er34gjf0') is not None:
                    size = i.find('span', class_='css-1x8agcm er34gjf0').text
                else:
                    size = 'Unknown'
                print(f"{name.text} - {price.text.split('.')[0]} - {city.text.split('-')[0]}")
                print(size)
                print(f"olx.ua{url}")
                        
                yield name.text, price.text.split('.')[0], city.text.split('-')[0], size, f"olx.ua{url}"
