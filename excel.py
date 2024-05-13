import xlsxwriter
from main import Parse
from main import GUI
from main import Logger
import config

#excel func
def writer(param):

    #put the path to save excel file
    book = xlsxwriter.Workbook(config.path)
    page = book.add_worksheet('Items')

    row = 0
    column = 0

    #setting width of cells
    page.set_column('A:A', 72)
    page.set_column('B:B', 12)
    page.set_column('C:C', 20)
    page.set_column('D:D', 20)
    page.set_column('F:F', 100)

    #writing data
    for item in param():
        page.write(row, column, item[0])
        page.write(row, column+1, item[1])
        page.write(row, column+2, item[2])
        page.write(row, column+3, item[3])
        page.write(row, column+4, item[4])
        row+=1

    book.close()

    gui = GUI()

#creating an instance of Parse class from main.py
parser = Parse()
#calling the func to start program
writer(parser.array)


    

