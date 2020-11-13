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
            if details[6] != 'NO EMAIL':
                SegField[1] = details[6].lower()
            
            for Purchaser in browser.find_elements_by_xpath('//*[@id="organizer-poptip"]/div/a'):
                Purchaser = Purchaser.get_attribute('innerText').strip()
                SegField[12] = Purchaser
                break
            Address = ''
            if details[9] != 'NO REGION':
                region = details[9]
                Address += f'{region}'

            if details[7] != 'NO NAME':
                Contact_name = details[7]
                Address += f'<br>\n{Contact_name}'
                
            if details[8] != 'NO PHONE':
                Phone = details[8]
                Address += f'<br>\nPhone: {Phone}'

            USREOU = ''
            if details[11] != 'NO USREOU':
                USREOU = details[11]
                Address += f'<br>\nUSREOU: {USREOU}'
                
            SegField[2] = Address

            SegField[13] = details[3]

            if details[10] != 'NO SITE':
                SegField[8] = details[10]

            SegField[19] = details[2]

            if str(details[4]) != 'NO DEADLINE':
                try:
                    datetime_object = datetime.strptime(str(details[4]), '%d.%m.%Y %H:%M')
                    Deadline = datetime_object.strftime("%Y-%m-%d")
                    SegField[24] = Deadline
                except:
                    try:
                        datetime_object = datetime.strptime(str(details[4]), '%d.%m.%Y')
                        Deadline = datetime_object.strftime("%Y-%m-%d")
                        SegField[24] = Deadline
                    except:pass
                
            Category = get_htmlSource_for_details.partition('Категорія</span>')[2].partition("</span>")[0].strip()
            Category = Category.partition('<span>')[2].strip()

            Form_of_bidding = get_htmlSource_for_details.partition('Форма проведення торгів</span>')[2].partition("</span>")[0].strip()
            Form_of_bidding = Form_of_bidding.partition('<span>')[2].strip()

            Tender_currency = get_htmlSource_for_details.partition('Валюта тендера</span>')[2].partition("</span>")[0].strip()
            Tender_currency = Tender_currency.partition('<span>')[2].strip()
            
            SegField[18] = f"{str(details[2])}<br>\nЄДРПОУ: {USREOU}<br>\nКатегорія: {Category}<br>\nФорма проведення торгів: {Form_of_bidding}<br>\nВалюта тендера: {Tender_currency}"

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
            
            if Category != "":
                copy_cpv = ""
                Cpv_status = True
                all_string = ""
                try:
                    while Cpv_status == True:
                        phoneNumRegex = re.compile(r'\d\d\d\d\d\d\d\d-')
                        CPv_main = phoneNumRegex.search(Category)
                        mainNumber = CPv_main.groups()
                        if CPv_main:
                            copy_cpv = CPv_main.group(), ", "
                            Category = Category.replace(CPv_main.group(), "")
                        else:
                            Cpv_status = False
                        result = "".join(str(x) for x in copy_cpv)
                        result = result.replace("-", "").strip()
                        result2 = result.replace("\n", "")
                        # print(result2)
                        all_string += result2.strip(",")
                except:
                    pass
                print(all_string.strip(","))
                SegField[36] = all_string
            else:
                SegField[36] = ""
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