# -*- coding: utf-8 -*-
from basic_functions import *
from lxml import html
from urllib.parse import quote
import demjson




def GetAdFromHrefKufar(href, title):
    try:

        text = GetPageText(quote(href, safe="%/:=&?~#+!$,;'@()*[]"))
        releaseDate = text[text.find('releaseDate'):text.find('releaseDate') + 50]
        releaseDate = releaseDate[releaseDate.find('=') + 2:releaseDate.find('/') - 1]
        releaseDate = datetime.datetime.strptime(releaseDate, "%Y-%m-%d %H:%M:%S")
        text = text[
               text.find('function pulseTrackPhoneNumberDisplayed(event)'):text.find(
                   'function pulseTrackAdReplySubmitted')]
        text = text[text.find('object'):text.find('});') + 1]

        # Converting JS object to DICT
        ADdict = demjson.decode("{" + text)

        # restructurizing DICT to one level
        del ADdict['origin']
        del ADdict['name']
        del ADdict['provider']
        del ADdict['type']
        del ADdict['deployStage']
        del ADdict['deployTag']
        ADdict['object']['inReplyTo']['cust_name'] = ADdict['object']['name']
        ADdict['object']['inReplyTo']['phone'] = ADdict['object']['telephone']
        ADdict = ADdict['object']['inReplyTo']
        ADdict['Region'] = ADdict['location']['addressRegion']
        ADdict['Subarea'] = ADdict['location']['addressSubarea']
        ADdict['href'] = href
        ADdict['title'] = title
        ADdict['release_timestamp'] = releaseDate
        del ADdict['location']
        return ADdict
    except Exception as e:
        DBPutLogMessage("GetAdFromHrefKufar(href,title) AD add failed link:" + href + ' ' + str(e))
        return []


def GetKufarAdList(page_text):
    # puts information from one of the kufar googs list page into DICT
    # input - text of listing page
    # outpout - list of dicts, each dict is one AD on listing page
    page = html.document_fromstring(page_text)

    AdList = page.find_class("list_ads__title")
    x = 0
    resultList = []
    for i in AdList:
        try:
            # extracting JajaScriptObject from page
            text = GetPageText(quote(i.get("href"), safe="%/:=&?~#+!$,;'@()*[]"))
            releaseDate = text[text.find('releaseDate'):text.find('releaseDate') + 50]
            releaseDate = releaseDate[releaseDate.find('=') + 2:releaseDate.find('/') - 1]
            releaseDate = datetime.datetime.strptime(releaseDate, "%Y-%m-%d %H:%M:%S")
            text = text[text.find('function pulseTrackPhoneNumberDisplayed(event)'):text.find(
                'function pulseTrackAdReplySubmitted')]
            text = text[text.find('object'):text.find('});') + 1]

            # Converting JS object to DICT
            ADdict = demjson.decode("{" + text)

            # restructurizing DICT to one level
            del ADdict['origin']
            del ADdict['name']
            del ADdict['provider']
            del ADdict['type']
            del ADdict['deployStage']
            del ADdict['deployTag']
            ADdict['object']['inReplyTo']['cust_name'] = ADdict['object']['name']
            ADdict['object']['inReplyTo']['phone'] = ADdict['object']['telephone']
            ADdict = ADdict['object']['inReplyTo']
            ADdict['Region'] = ADdict['location']['addressRegion']
            ADdict['Subarea'] = ADdict['location']['addressSubarea']
            ADdict['href'] = i.get("href")
            ADdict['title'] = i.text_content()
            ADdict['release_timestamp'] = releaseDate
            del ADdict['location']
            resultList.append(ADdict)
        except Exception as e:

            DBPutLogMessage("GetKufarADList() AD add failed link:" + i.get("href") + ' ' + str(e))

    return resultList


def CheckAdStateKufar(href):
    text = GetPageText(quote(href, safe="%/:=&?~#+!$,;'@()*[]"))
    if text.find('Объявление не найдено') != -1:  # if deleted or expired
        return [href, 'sold']

    else:  # if no AD page displayed
        text = text[text.find('function pulseTrackPhoneNumberDisplayed(event)'):text.find(
            'function pulseTrackAdReplySubmitted')]
        if len(text) == 0:
            return [href, 'disappeared']

        else:  # if AD in normal state exist
            return [href, 'exists']



def GetAdHrefsRealt(page_num):
    page_text = GetPageText('https://realt.by/rent/offices/?page='+str(page_num))


    if page_text.find('Расширенный поиск в Минске и Минской области') == -1:
        page = html.document_fromstring(page_text)
        AdList = page.find_class("bd-item")
        ResultList = []


        for Ad in AdList:
            try:
                ResultList.append({'href': Ad.find_class('title')[0][0].get('href'),
                                   'title': clearString(Ad.find_class('title')[0][0].text)})
            except:
                continue
        return ResultList
    else:
        return []


def GetAdFromLink(ad):
    result = {}
    page_text = GetPageText(ad['href'])
    page = html.document_fromstring(page_text)

    result['href']=ad['href']
    result['title']=ad['title']
    # Page views
    view = page.find_class('views-control')
    view = view[0].text_content()
    view = int(view[view.find('за последние 7 дней – ') + len('за последние 7 дней – '):])
    result['views'] = view

    # Price
    price = page.find_class('f14')[1].text_content().replace("\xa0", '')

    if price.find("договорная")!=-1:
        price = 0
    elif (price.find('руб/кв.м')!=-1):
        price=price.split(" ")
        for p in price:
            if p.find('руб/кв.м')!=-1:
                price=p.replece('руб/кв.м','')
                break

    elif (price.find('руб')!=-1):
        price=price


    result['price'] = price

    return (result)



for i in range (1,100):
    list=GetAdHrefsRealt(i)
    for ad in list:
        res=GetAdFromLink(ad)
        print(res['price'],res['href'])









