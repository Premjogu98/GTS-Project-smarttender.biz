from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import html
import sys, os
from datetime import datetime,timedelta
import Global_var
import wx
import string
import html
import re
from Scraping_things import scrap_data
app = wx.App()

def ChromeDriver():
    browser = webdriver.Chrome(executable_path=str(f"C:\\chromedriver.exe"))
    browser.maximize_window()
    browser.get("https://smarttender.biz/komertsiyni-torgy/?s=3")
    time.sleep(5)
    tender_details_list = []
    page_count = 2
    while True:
        list_count = 0
        for publish_date in browser.find_elements_by_class_name('trade-published'):
            publish_date_text = publish_date.get_attribute('innerText').strip()

            datetime_object_pub = datetime.strptime(str(publish_date_text), '%d.%m.%Y')
            User_Selected_date = datetime.strptime(str(Global_var.date), '%d.%m.%Y')
            timedelta_obj = datetime_object_pub - User_Selected_date
            day = timedelta_obj.days
            if day >= 0:
                detail_list = []
                detail_list.append(publish_date_text)
                tender_detail = browser.find_elements_by_xpath('//*[@data-qa="trade-subject-title"]/a')
                tender_href_href = tender_detail[list_count].get_attribute('href').strip()
                detail_list.append(tender_href_href)

                tender_href_text = tender_detail[list_count].get_attribute('innerText').strip()
                detail_list.append(tender_href_text)
                
                tender_id = browser.find_elements_by_xpath('//*[@class="padding-top-15 trade-number"]')
                tender_id = tender_id[list_count].get_attribute('innerText').strip()
                tender_id_text = tender_id.partition("№")[2].partition(".")[0]
                detail_list.append(tender_id_text)

                deadline = browser.find_elements_by_xpath('//*[@class="trade-status-date"]')
                deadline_text = deadline[list_count].get_attribute('innerText').replace('до','').strip()
                if deadline_text != '':
                    detail_list.append(deadline_text)
                else:
                    detail_list.append('NO DEADLINE')

                Amount = browser.find_elements_by_xpath('//*[@class="trade-initial-rate text-center"]')
                Amount_text = Amount[list_count].get_attribute('innerText').strip()
                if 'Бюджет' not in Amount_text:
                    Amount_text = Amount_text.partition("₴")[0].replace(' ','').replace(',','.')
                    detail_list.append(Amount_text)
                else:
                    detail_list.append('NO AMOUNT')

                try:
                    email = browser.find_elements_by_xpath('//*[@data-qa="commercial-trade-organizer-email"]')
                    email_text = email[list_count].get_attribute('innerText').strip()
                    if email_text != '':
                        detail_list.append(email_text)
                    else:
                        detail_list.append('NO EMAIL')
                except:
                    detail_list.append('NO EMAIL')

                try:
                    organizer_name = browser.find_elements_by_xpath('//*[@data-qa="commercial-trade-organizer-name"]')
                    organizer_name_text = organizer_name[list_count].get_attribute('innerText').strip()
                    if organizer_name_text != '':
                        detail_list.append(organizer_name_text)
                    else:
                        detail_list.append('NO NAME')
                except:
                    detail_list.append('NO NAME')

                try:
                    phone = browser.find_elements_by_xpath('//*[@data-qa="commercial-trade-organizer-phone"]')
                    phone_text = phone[list_count].get_attribute('innerText').strip()
                    if phone_text != '':
                        detail_list.append(phone_text)
                    else:
                        detail_list.append('NO PHONE')
                except:
                    detail_list.append('NO PHONE')

                try:
                    region = browser.find_elements_by_xpath('//*[@data-qa="commercial-trade-organizer-region"]')
                    region_text = region[list_count].get_attribute('innerText').strip()
                    if region_text != '':
                        region_text = region_text.partition(':')[2].strip()
                        detail_list.append(region_text)
                    else:
                        detail_list.append('NO REGION')
                except:
                    detail_list.append('NO REGION')

                try:
                    site = browser.find_elements_by_xpath('//*[@data-qa="commercial-trade-organizer-site"]/a')
                    site_text = site[list_count].get_attribute('href').strip()
                    if site_text != '':
                        detail_list.append(site_text)
                    else:
                        detail_list.append('NO SITE')
                except:
                    detail_list.append('NO SITE')

                try:
                    usreou = browser.find_elements_by_xpath('//*[@data-qa="commercial-trade-organizer-usreou"]')
                    usreou_text = usreou[list_count].get_attribute('innerText').strip()
                    if usreou_text != '':
                        usreou_text = usreou_text.partition(':')[2].strip()
                        detail_list.append(usreou_text)
                    else:
                        detail_list.append('NO USREOU')
                except:
                    detail_list.append('NO USREOU')
                tender_details_list.append(detail_list)
                list_count +=1
            else:
                collect_links(browser, tender_details_list)
            
        browser.get(f"https://smarttender.biz/komertsiyni-torgy/?s=3&p={str(page_count)}")
        page_count +=1
        time.sleep(3)

def collect_links(browser, tender_details_list):
    Global_var.Total = len(tender_details_list)
    for details in tender_details_list:
        browser.get(str(details[1]))
        time.sleep(2)
        get_htmlSource = ''
        for get_htmlSource in browser.find_elements_by_xpath('//*[@id="commercial-detail"]'):
            get_htmlSource = get_htmlSource.get_attribute('outerHTML').strip()
            get_htmlSource = get_htmlSource.replace('display: none;','display: block;').replace('none;','block;').replace('Прийом пропозицій','')
            attachment_html_text = '<span>'
            attachment_count = 1
            for attachment in browser.find_elements_by_xpath('//*[@data-qa="file-preview"]'):
                attachment_text = attachment.get_attribute('outerHTML').replace('\n',' ').strip()
                attachment_text = re.sub('\s+', ' ', attachment_text)
                attachment_href = attachment_text.partition('data-qa-href="')[2].partition('"')[0]
                attachment_html_text += f'<a href="{str(attachment_href)}"><h4> Click Here For Attachment No {str(attachment_count)}</h4></a>'
                attachment_count += 1
            attachment_html_text += '</span>'
            get_htmlSource = f'{get_htmlSource}{attachment_html_text}'
            break
        scrap_data(browser,details,get_htmlSource)
        print(f'Total: {str(Global_var.Total)} Deadline Not given: {Global_var.deadline_Not_given} duplicate: {Global_var.duplicate} inserted: {Global_var.inserted} expired: {Global_var.expired} QC Tenders: {Global_var.QC_Tenders}')

    wx.MessageBox(f'Total: {str(Global_var.Total)}\nDeadline Not given: {Global_var.deadline_Not_given}\nduplicate: {Global_var.duplicate}\ninserted: {Global_var.inserted}\nexpired: {Global_var.expired}\nQC Tenders: {Global_var.QC_Tenders}','smarttender.biz', wx.OK | wx.ICON_INFORMATION)
    browser.close()
    sys.exit()

ChromeDriver()