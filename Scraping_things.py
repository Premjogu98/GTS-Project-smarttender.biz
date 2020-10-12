import time
from datetime import datetime
import Global_var
from Insert_On_Datbase import insert_in_Local,create_filename
import sys , os
import string
import time
from datetime import datetime
import html
import re

def scrap_data(browser,details,get_htmlSource):

    SegField = []
    for data in range(45):
        SegField.append('')

    get_htmlSource = html.unescape(str(get_htmlSource))
    get_htmlSource_for_details = get_htmlSource.replace('\n','')
    get_htmlSource_for_details = re.sub('\s+', ' ', get_htmlSource)
    
    a = True
    while a == True:
        try:
            Email = get_htmlSource_for_details.partition('e-mail:')[2].partition("</a>")[0].strip()
            Email = Email.partition('mailto:')[2].partition('"')[0].strip().replace(';',' , ')
            Email_regex = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+\.[a-zA-Z]+)", Email)
            try:
                SegField[1] = Email_regex[0].lower()
            except:
                SegField[1] = ''
            
            for Purchaser in browser.find_elements_by_xpath('//*[@id="organizer-poptip"]/div/a'):
                Purchaser = Purchaser.get_attribute('innerText').strip()
                SegField[12] = Purchaser
                break

            Contact_details_outerhtml = get_htmlSource_for_details.partition('ПІБ</span>')[2].partition("</li>")[0].strip()
            Contact_details_outerhtml = Contact_details_outerhtml.partition('">')[2].partition("</span>")[0].strip()
            Contact_name = Contact_details_outerhtml.partition('<span>')[2].strip()
            Contact_name = re.sub('\s+', ' ', Contact_name)

            Phone = get_htmlSource_for_details.partition('Телефон:')[2].partition("</a>")[0].strip()
            Phone = Phone.partition('">')[2].strip()
            Address = f'{Contact_name}<br>\nPhone: {Phone}<br>\nEmail: {SegField[1]}'
            SegField[2] = Address

            SegField[13] = details[3]
   
            SegField[19] = details[2]
            if str(details[4]) != 'NO DEADLINE':
                datetime_object = datetime.strptime(str(details[4]), '%d.%m.%Y %H:%M')
                Deadline = datetime_object.strftime("%Y-%m-%d")
                SegField[24] = Deadline

            
            USREOU = get_htmlSource_for_details.partition('ЄДРПОУ</span>')[2].partition("</span>")[0].strip()
            USREOU = USREOU.partition('<span>')[2].strip()
            
            Category = get_htmlSource_for_details.partition('Категорія</span>')[2].partition("</span>")[0].strip()
            Category = Category.partition('<span>')[2].strip()

            Form_of_bidding = get_htmlSource_for_details.partition('Форма проведення торгів</span>')[2].partition("</span>")[0].strip()
            Form_of_bidding = Form_of_bidding.partition('<span>')[2].strip()

            Tender_currency = get_htmlSource_for_details.partition('Валюта тендера</span>')[2].partition("</span>")[0].strip()
            Tender_currency = Tender_currency.partition('<span>')[2].strip()
            
            SegField[18] = f"{str(SegField[19])}<br>\nЄДРПОУ: {USREOU}<br>\nКатегорія: {Category}<br>\nФорма проведення торгів: {Form_of_bidding}<br>\nВалюта тендера: {Tender_currency}"

            SegField[28] = details[1]

            SegField[31] = 'smarttender.biz'
            SegField[7] = "UA"
            SegField[14] = '2'
            SegField[16] = '1'
            if details[5] != 'NO AMOUNT':
                if 'Гривня' in Tender_currency:
                    SegField[20] = details[5].strip()
                    SegField[21] = "UAH" 
            SegField[42] = SegField[7]
            SegField[43] = ""
            for SegIndex in range(len(SegField)):
                print(SegIndex, end=' ')
                print(SegField[SegIndex])
                SegField[SegIndex] = html.unescape(str(SegField[SegIndex]))
                SegField[SegIndex] = str(SegField[SegIndex]).replace("'", "''")

            if len(SegField[19]) >= 200:
                SegField[19] = str(SegField[19])[:200]+'...'

            if len(SegField[18]) >= 1500:
                SegField[18] = str(SegField[18])[:1500]+'...'

            if SegField[19] == '':
                wx.MessageBox(' Short Desc Blank ','smarttender.biz', wx.OK | wx.ICON_INFORMATION)
            else:
                check_date(get_htmlSource, SegField)
                # create_filename(get_htmlSource , SegField)
                pass
            a = False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",
                  exc_tb.tb_lineno)
            a = True
            time.sleep(5)


def check_date(get_htmlSource, SegField):
    a = 0
    while a == 0:
        tender_date = str(SegField[24])
        nowdate = datetime.now()
        date2 = nowdate.strftime("%Y-%m-%d")
        try:
            if tender_date != '':
                deadline = time.strptime(tender_date , "%Y-%m-%d")
                currentdate = time.strptime(date2 , "%Y-%m-%d")
                if deadline > currentdate:
                    insert_in_Local(get_htmlSource, SegField)
                    a = 1
                else:
                    print("Tender Expired")
                    Global_var.expired += 1
                    a = 1
            else:
                print("Deadline was not given")
                Global_var.deadline_Not_given += 1
                a = 1
        except Exception as e:
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            exc_type , exc_obj , exc_tb = sys.exc_info()
            print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname , "\n" , exc_tb.tb_lineno)
            a = 0