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
    page_text = GetPageText('https://realt.by/rent/offices/?view='+str(page_num)+'#tabs')

    if page_text.find('Ничего не найдено, поиск расширен') == -1:
        page = html.document_fromstring(page_text)
        AdList = page.find_class("list_ads__title")
        ResultList = []
        for Ad in AdList:
            try:
                ResultList.append({'href': quote(Ad.get('href'), safe="%/:=&?~#+!$,;'@()*[]"),
                                   'title': clearString(Ad.text_content())})
            except:
                continue
        return ResultList
    else:
        return []
