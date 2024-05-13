from bs4 import BeautifulSoup
import requests
from time import sleep
import tkinter as tk
from tkinter import ttk
import openpyxl
import logging
import config

class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, filename="logs.log",filemode="a", format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')
    
    @staticmethod
    def log_url(url):
        logging.info(f'Request to "{url}"')

    @staticmethod
    def log_pages(num):
            logging.info(f'Found pages: {num}')

    @staticmethod
    def log_items(num):
        if num >= 1000:
            logging.info(f'Found items: more than 1000')
        else:
            logging.info(f'Found items: {num}')

class Parse:
    def __init__(self):
        self.user_input = str(input('Enter what you want to parse.. '))
        self.user_input = self.user_input.replace(' ', '-')
        self.url = f'https://www.olx.ua/uk/list/q-{self.user_input}/'
        self.logger = Logger()
        self.logger.log_url(self.url)

        #put your headers here
        self.headers = {'User-Agent': config.user_agent}


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
        try:
            page_numbers = []
            last_page = self.get_data(url).findAll('a', class_='css-1mi714g')

            for i in last_page:
                page_number = int(i.text.strip())
                page_numbers.append(page_number)

            last_page_number = max(page_numbers)
        except ValueError:
            last_page_number = 1

        self.logger.log_pages(int(last_page_number))
        return int(last_page_number)
    
    def get_numbers_of_ads(self, url):
        num_ad = self.get_data(url).find('span', class_='css-7ddzao')
        if len(num_ad.text.split()) == 6:
            self.logger.log_items(1000)
            return 1000
        else:
            self.logger.log_items(int(num_ad.text.split()[-2]))
            return int(num_ad.text.split()[-2].strip())
    
    # finding all required attributes
    def array(self):
        scrolled_elements = 1
        base_url = f'https://www.olx.ua/uk/list/q-{self.user_input}/'
        num_ads = self.get_numbers_of_ads(base_url)

        
        for j in range(1, self.get_last_page(base_url) + 1):
            sleep(1)
            url = f'https://www.olx.ua/uk/list/q-{self.user_input}/?page={j}'
            self.get_data(url)

            for i in self.get_cards(url):
                name = i.find('h6', class_='css-16v5mdi er34gjf0')
                price = i.find('p', class_='css-tyui9s er34gjf0')
                city = i.find('p', class_='css-1a4brun er34gjf0')
                url = i.find('a', class_='css-z3gu2d').get('href')
                if i.find('span', class_='css-1x8agcm er34gjf0') is not None:
                    size = i.find('span', class_='css-1x8agcm er34gjf0').text
                else:
                    size = 'Unknown'
                try:
                    yield name.text, price.text.split('.')[0], city.text.split('-')[0], size, f"olx.ua{url}"
                except AttributeError:
                    yield name.text, 'Послуга', city.text.split('-')[0], size, f"olx.ua{url}"
                
                # Если количество проскролленных объявлений достигло точного значения, прекратить скроллинг
                if num_ads < 1000 and scrolled_elements >= num_ads:
                    break
                scrolled_elements += 1

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Olx')
        self.style = ttk.Style(self.root)
        self.root.tk.call('source', 'forest-light.tcl')
        self.root.tk.call('source', 'forest-dark.tcl')
        self.style.theme_use('forest-dark')

        self.frame = ttk.Frame(self.root)
        self.frame.pack()

        self.widgets_frame = ttk.LabelFrame(self.frame, text='Filter')
        self.widgets_frame.grid(row=0,column=0, padx=20)

        self.name_label = ttk.Label(self.widgets_frame, text='Olx parser')
        self.name_label.grid(row=0, column=0, sticky='ew', padx=5, pady=(0, 5))

        self.checked = tk.BooleanVar()
        self.checkedbutton = ttk.Checkbutton(self.widgets_frame, text='Sized', variable=self.checked, command=self.checkboxer)
        self.checkedbutton.grid(row=1, column=0, sticky='nwes', padx=5, pady=5)

        self.copyright_label = ttk.Label(self.widgets_frame, text='©2024 leshayq')
        self.copyright_label.grid(row=2, column=0, sticky='ew', padx=5, pady=(10, 5))

        self.separator = ttk.Separator(self.widgets_frame)
        self.separator.grid(row=3, column=0, padx=(20,10), pady=10, sticky='ew')

        self.mode_switch = ttk.Checkbutton(self.widgets_frame, text='Mode', style='Switch', command=self.toggle_mode)
        self.mode_switch.grid(row=4, column=0, padx=5, pady=10, sticky='nsew')

        self.treeFrame = ttk.Frame(self.frame)
        self.treeFrame.grid(row=0, column=1, pady=10)

        self.treeScroll = ttk.Scrollbar(self.treeFrame)
        self.treeScroll.pack(side='right', fill='y')

        cols = ('Name', 'Price', 'City', 'Size', 'Url')
        self.treeview = ttk.Treeview(self.treeFrame, show='headings', columns=cols, height=13, yscrollcommand=self.treeScroll.set)
        self.treeview.column('Name', width=220)
        self.treeview.column('Price', width=70)
        self.treeview.column('City', width=120)
        self.treeview.column('Size', width=70)
        self.treeview.column('Url', width=250)
        self.treeview.pack()
        self.treeScroll.config(command=self.treeview.yview)

        self.load_data()

        self.root.mainloop()

    def toggle_mode(self):
        if self.mode_switch.instate(['selected']):

            self.style.theme_use('forest-light')
        else:
            self.style.theme_use('forest-dark')

    def load_data(self):
        path = r"C:\Users\olesh\OneDrive\Рабочий стол\olx-parser\data.xlsx"
        workbook = openpyxl.load_workbook(path)
        sheet = workbook.active

        list_values = list(sheet.values)


        self.treeview.heading('Name', text='Name')
        self.treeview.heading('Price', text='Price')
        self.treeview.heading('City', text='City')
        self.treeview.heading('Size', text='Size')
        self.treeview.heading('Url', text='Url')
        
        if self.checked.get():
            self.treeview.delete(*self.treeview.get_children())
            for value_tuple in list_values:
                if value_tuple[3] != 'Unknown':
                    self.treeview.insert('', tk.END, values=value_tuple)
        else:
            self.treeview.delete(*self.treeview.get_children())
            for value_tuple in list_values:
                self.treeview.insert('', tk.END, values=value_tuple)


    def checkboxer(self):
        self.load_data()