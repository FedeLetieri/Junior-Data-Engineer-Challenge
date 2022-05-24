from urllib import request
from bs4 import BeautifulSoup
from datetime import datetime
import csv


#
# Extract the Farm Price, Wholesale Price and Retail Price from
# https://www.fama.gov.my/en/harga-pasaran-terkini
#


def read_html(url):
    result = []
    response = request.urlopen(url)
    soup = BeautifulSoup(response,
                         features="html.parser")
    table = soup.findAll("tr",
                         align="center")
    body = table[0].findAllNext("td")

    for data in body:
        result.append(data.text.replace("KILOGRAM", "KG"))
    response.close()
    return result


#
# Rearrange the data in group of enter, Variety Name, Grade, Unit,
# Maximum Price, Average Price and Minimum Price
#


def data_arrange(data_list):
    id = 0
    parent = []
    children = []
    grands = []
    title = ""
    for data in data_list:
        if "Pusat" in data:
            title = data.split(':')[1].split(',')[0].strip()
            if children:
                id = 0
                grands.insert(0, title)
                children.append(grands)
                grands = []
                parent.append(children)
                children = []
            continue

        if "Gred" in data \
                or "Unit" in data \
                or "Harga" in data \
                or "Tinggi" in data \
                or "Purata" in data \
                or "Rendah" in data \
                or "Nama Varieti" in data:
            continue

        if id >= 6:
            id = 0
            grands.insert(0, title)
            children.append(grands)
            grands = []
        grands.append(data)
        id += 1

    # Update last children
    parent.append(children)

    return parent


#
# Convert the list to dictionary datatype
# for CSV format
#


def list_to_dict(data_list, market_price_type):
    dict = {}
    dict_list = []

    for level_1 in data_list:
        for level_2 in level_1:
            dict["Market Price Type"] = market_price_type
            dict["Center"] = level_2[0]
            dict["Variety Name"] = level_2[1]
            dict["Grade"] = level_2[2]
            dict["Unit"] = level_2[3]
            dict["Max Price"] = level_2[4]
            dict["Average Price"] = level_2[5]
            dict["Min Price"] = level_2[6]
            dict_list.append(dict)
            dict = {}

    return dict_list


def generate_csv(data_list):
    filedate = "fama_" + str(dt.year) + str(dt.month) + str(dt.day - 1) + ".csv"
    keys = ["Market Price Type", "Center", "Variety Name", "Grade", "Unit", "Max Price", "Average Price", "Min Price"]

    try:
        with open(filedate, "w+") as write_fama:
            writer = csv.DictWriter(write_fama, fieldnames=keys, lineterminator='\n')
            writer.writeheader()
            writer.writerows(data_list)
        print(filedate + " had successfully generated")

    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))


if __name__ == '__main__':
    dt = datetime.today().date()
    date = str(dt.year) + "/" + str(dt.month) + "/" + str(dt.day - 1)
    prev_date = str(dt.year) + "/" + str(dt.month) + "/" + str(dt.day - 3)
    URL_Farm = "https://sdvi2.fama.gov.my/price/direct/price/daily_commodityRpt.asp?Pricing=A&LevelCd=04"
    URL_Retail = "https://sdvi2.fama.gov.my/price/direct/price/daily_commodityRpt.asp?Pricing=A&LevelCd=01"
    URL_Wholesale = "https://sdvi2.fama.gov.my/price/direct/price/daily_commodityRpt.asp?Pricing=A&LevelCd=03"

    price_farm = read_html(URL_Farm)
    price_farm = price_farm[1:-1]
    list_price_farm = data_arrange(price_farm)
    dict_list_farm = list_to_dict(list_price_farm, "Farm Price")

    price_wholesale = read_html(URL_Wholesale)
    price_wholesale = price_wholesale[1:-1]
    list_pric_wholesale = data_arrange(price_wholesale)
    dict_list_wholesale = list_to_dict(list_pric_wholesale, "Wholesale Price")

    price_retail = read_html(URL_Retail)
    price_retail = price_retail[1:-1]
    list_price_retail = data_arrange(price_retail)
    dict_list_retail = list_to_dict(list_price_retail, "Retail Price")

    csv_list = dict_list_farm + dict_list_wholesale + dict_list_retail
    generate_csv(csv_list)
