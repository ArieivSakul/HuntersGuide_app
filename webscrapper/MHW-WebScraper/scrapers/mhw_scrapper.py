from dataclasses import dataclass
from itertools import count, takewhile
from typing import Final
from unicodedata import normalize as u_normalize
from io import StringIO
from enum import Enum
from webbrowser import get

from bs4 import BeautifulSoup
from bs4 import Tag
from construct import Switch
import requests


@dataclass
class URI_TYPES:
    @dataclass
    class MONSTERS:
        MAIN_PAGE = 'Monsters'
        LARGE_MOSTERS = 'Large+Monsters'
        SMALL_MONSTER = 'Small+Monsters'

class Utils:
    BC_CONTAINER_ID: Final[str] = 'breadcrumbs-container'

    @staticmethod
    def breadcrumbs_container_to_path(soupTag: Tag) -> str:
        if soupTag['id'] != Utils.BC_CONTAINER_ID:
            pass
        path = ''
        for childen in soupTag:
            if isinstance(childen, Tag):
                if childen.name != 'a':
                    continue
                path += childen.text
            else:
                path += u_normalize('NFKD', childen.text).replace(' ', '')
        return path.replace('\n','')

def scrape(baseUrl: str, uri: str) -> list:
    url = f'{baseUrl}/{uri}'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    if uri == URI_TYPES.MONSTERS.MAIN_PAGE:
        return scrape_monster_types(soup, baseUrl)
    else:
        pass

def scrape_monsters_page_infobox(infobox_soup: Tag) -> dict:
    if infobox_soup == None:
        return None
    table = infobox_soup.find('table', {'class': 'wiki_table'})
    table_headers = table.find_all('th')
    entity_name = table_headers[0]
    try:
        entity_name = entity_name.find('h3').text
    except:
        try:
            entity_name = entity_name.find('h2').text
        except:
            entity_name = entity_name.text
    
    # Discard first element; It's the header - ASSUMPTION
    table_rows = table.find_all('tr')[1:]
    img_src = None

    imgIdx = 1
    for table_row in table_rows:
        imgTag = table_row.find('img')
        if imgTag is not None:
            img_src = imgTag['src']
            break
        else:
            imgIdx += 1

    if img_src != None:
        # The intity attribs are usualy after the img - ASSUMPTION
        table_rows = table_rows[imgIdx:]

    entity_attributes = {
        'img': img_src,
        'name': u_normalize('NFKD', entity_name)
    }
    
    for row in table_rows:
        row_data = row.find_all('td')
        entity_attributes[row_data[0].text] = u_normalize('NFKD', ''.join(data.text for data in row_data[1:]))
    
    return entity_attributes

def scrape_monsters_page_mainContent(mainContent_soup: Tag) -> str:
    if mainContent_soup == None:
        return
    dumbParser = DumbHtml2Markdown(mainContent_soup)
    return dumbParser.parse()

def scrape_monster_page_data(page_soup: BeautifulSoup) -> dict:
    npc_data = {}
    infobox = scrape_monsters_page_infobox(page_soup.find('div', {'id': 'infobox'} | {'class': 'infobox'}))
    if infobox == None:
        return None
    npc_data['name'] = infobox.get('name')
    npc_data['infoTable'] = infobox
    npc_data['mainContent'] = scrape_monsters_page_mainContent(page_soup.find('div', {'id': 'wiki-content-block'}))
    return npc_data

def scrape_link(href: str, baseUrl: str):
    url = f'{baseUrl}{href}'
    page = requests.get(url)
    print(f'scrapping link \'{url}\'... | request code: {page.status_code}')
    if(page.status_code != 200):
        return {}
    
    page_soup = BeautifulSoup(page.content, 'html.parser')
    return scrape_monster_page_data(page_soup)

def scrape_monster_card_item(card_item: Tag, baseUrl: str):
    linkTag = None
    for tag in list(map(lambda tag: filter(lambda cTag: isinstance(cTag, Tag), tag.contents), card_item.find_all('h4'))):
        linkTag = next((i for i in tag if i.get('href')), None)
        if linkTag is not None:
            break
    if linkTag is None: # Empty card
        return
    return scrape_link(linkTag['href'], baseUrl)

def scrape_small_monsters(soup: BeautifulSoup, baseUrl):
    rowDivs = soup.find('div', {'id': 'wiki-content-block'}).find_next('h3', {'class': 'titlearea'}).find_all_next('div', {'class': 'row'})
    cards = []
    for cardRow in rowDivs:
        for card in cardRow.find_all('div', {'class': 'col-sm-4'}):
            cards.append(card)
    return [
        scrape_monster_card_item(card_item, baseUrl)
        for card_item
        in cards
    ]

def scrape_large_monster(soup: BeautifulSoup, baseUrl: str):
    rowDivs = soup.find('div', {'id': 'wiki-content-block'}).find_next('h3', {'class': 'special'}).find_all_next('div', {'class': 'row'})
    cards = []
    for cardRow in rowDivs:
        for card in cardRow.find_all('div', {'class': 'col-sm-4'}):
            cards.append(card)
    return [
        scrape_monster_card_item(card_item, baseUrl)
        for card_item
        in cards
    ]

def scrape_monster_types(soup: BeautifulSoup, baseUrl: str) -> list:
    monsters = {}
    buttons = soup.find('div', { 'id': 'wiki-content-block'}).find_all('a', { 'class': 'btn btn-default fullwidth'})
    for btn in buttons:
        href = btn['href']
        page = requests.get(baseUrl + href)
        if page.status_code >= 400:
            continue
        match href[1:]:
            case URI_TYPES.MONSTERS.SMALL_MONSTER:
                monsters['SmallMonsters'] = scrape_small_monsters(BeautifulSoup(page.content, 'html.parser'), baseUrl)
            case URI_TYPES.MONSTERS.LARGE_MOSTERS:
                monsters['LargeMonsters'] = scrape_large_monster(BeautifulSoup(page.content, 'html.parser'), baseUrl)
    return monsters


class DumbHtml2Markdown:
    _buffer: StringIO
    _rootTag: Tag

    suported_tags: Final[list] = ['h1', 'h2', 'h3', 'ul', 'ol', 'li', 'em', 'p', 'a', 'strong', 'br']

    def __init__(self, soup: Tag):
        self._buffer = StringIO()
        self._rootTag = soup
    
    def parse(self) -> str:
        self.__writeTag(self._rootTag)
        return self._buffer.getvalue()

    def __writeText(self, text: str, tag: Tag):
        if text == '\n':
            return
        if len(tag.contents) == 1:
            if isinstance(tag.previous, Tag):
                text = text.lstrip()
            if isinstance(tag.next, Tag):
                text = text.rstrip()
        self._buffer.write(u_normalize('NFKD', text))

    def __writeEndl(self):
        self._buffer.write('\r\n')

    def __writeBreakLine(self):
        self._buffer.write('\\')
        self.__writeEndl()

    def __writeHighligthed(self, tag: Tag):
        self._buffer.write('`')
        self.__writeTag(tag)
        self._buffer.write('`')
    
    def __writeBlockquote(self, tag: Tag):
        self._buffer.write('>')
        self.__writeTag(tag)
        self.__writeEndl()

    def __writeParagraph(self, tag: Tag):
        self.__writeEndl()
        self.__writeTag(tag)
        self.__writeEndl()

    def __writeUnordedList(self, tag: Tag, blockQuote = False):
        if blockQuote:
            self.__writeBlockquote(tag)
        else:
            self.__writeTag(tag)

    def __writeOrderedList(self, tag: Tag, blockQuote = False):
        if blockQuote:
            self.__writeBlockquote(tag)
        else:
            self.__writeTag(tag)

    def __writeListItem(self, tag: Tag):
        isList = lambda tag: tag.name == 'ul' or tag.name == 'ol'
        depth = sum(1 for _ in takewhile(isList, tag.parents)) - 1
        if depth < 0:
            self.__writeTag(tag)
            return
        if depth > 0:
            self._buffer.write('\t' * depth)
        match tag.parent.name:
            case 'ul':
                self._buffer.write('- ')
            case 'ol':
                self._buffer.write('1. ')
        self.__writeTag(tag)
        self.__writeEndl()

    def __writeItalic(self, tag: Tag):
        self._buffer.write('*')
        self.__writeTag(tag)
        self._buffer.write('*')

    def __writeHeading(self, tag: Tag):
        self._buffer.write(''.join('#' for i in range(0 ,int(tag.name[1]))))
        self._buffer.write(' ')
        self.__writeTag(tag)
        self.__writeEndl()

    def __writeBold(self, tag: Tag):
        self._buffer.write('**')
        self.__writeTag(tag)
        self._buffer.write('**')

    def __writeTag(self, tag: Tag):
        for item in tag.contents:
            if isinstance(item, Tag):
                if any(item.name == tname for tname in self.suported_tags):
                    match item.name:
                        case 'p':
                            self.__writeParagraph(item)
                        case 'ul':
                            self.__writeUnordedList(item)
                        case 'ol':
                            self.__writeOrderedList(item)
                        case 'li':
                            self.__writeListItem(item)
                        case 'a':
                            self.__writeHighligthed(item)
                        case 'em':
                            self.__writeItalic(item)
                        case 'br':
                            self.__writeBreakLine()
                        case 'strong':
                            self.__writeBold(item)
                    if item.name[0] == 'h':
                        self.__writeHeading(item)
            else:
                self.__writeText(item.text, tag)

    def __del__(self):
        self._buffer.close()