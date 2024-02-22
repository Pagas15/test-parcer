# Он отказался от рефакторинга, ничего не знаю

import requests
import time
from random import randint
from bs4 import BeautifulSoup
from threading import Thread
from multiprocessing import Process
import json

import telebot

bot = telebot.TeleBot('7136448187:AAHhqSCwT_vo1c4FQfQWofjBDGoiNem0M8s')

user_list = [ "707025315", ]


class MessageException( Exception ):

    def __init__(self, message : str, *args: object) -> None:
        self.message = message
        super().__init__(*args)

class Link:
    def __init__(self, url, find_kwargs : dict = { "name" : "body" }, _is_working = True, _warning = False, _warning_messages = [] ) -> None:
        self.url : str = url
        self.is_working : bool = _is_working
        self.warning : bool = _warning
        self.warning_messages = _warning_messages
        self.find_kwargs : str = find_kwargs

def parse_links() -> list[Link]:
    result = []
    f = open( "links.json", "r" )
    f_content = f.read()

    t_d : dict = json.loads( f_content )

    for v in t_d.values():
        t_o = Link( url = v[ "url" ], find_kwargs=v["find_kwargs"], _is_working = v["is_working"], _warning = v["warning"], _warning_messages = v["warning_messages"] )

        result.append( t_o )

    
    f.close()
    return result 

def load_links( links : list[Link] ) -> None:
    f = open( "links.json", "w" )
    j = {}

    for i in range(len(links)):
        obj = links[i]

        j.update( { i : { "url" : obj.url, "find_kwargs" : obj.find_kwargs, "is_working" : obj.is_working, "warning" : obj.warning, "warning_messages" : obj.warning_messages } } )
    
    j = json.dumps( j )
    f.write( j )

    f.close()

def delete_link( link_id : int ) -> None:
    links = parse_links()

    links.pop( link_id )

    load_links( links )

def add_link( link : Link ) -> None:
    links = parse_links()

    links.append( link )

    load_links( links )

def change_link( link_id : int, **kwargs ) -> None:
    links = parse_links()

    current_link = links[link_id]

    for k, v in kwargs.items():
        if k == "is_working":
            current_link.is_working = bool(int(v))
        elif k == "warning":
            current_link.warning = bool(int(v))
        elif k == "find_kwargs":
            current_link.find_kwargs = json.loads( v )
        elif k == "url":
            current_link.url = v
        elif k == "warning_messages":
            current_link.warning_messages = v

    links.pop( link_id )
    links.insert( link_id, current_link )

    load_links( links )






# urls = [ 'https://x.ai/', 'https://openai.com/research', 'https://openai.com', 'https://www.microsoft.com/en-us/research/', 'https://www.amazon.science/publications/', 'https://www.spacex.com/', 'https://www.spacex.com/updates/', 'https://www.boringcompany.com/', 'https://www.boringcompany.com/projects', 'https://www.tesla.com/', 'https://neuralink.com/', 'https://neuralink.com/blog/', 'https://openai.com/blog', 'https://blog.google/technology/ai', 'https://vitalik.eth.limo', 'https://www.nvidia.com/en-us/', 'https://blogs.nvidia.com/', 'https://www.amd.com/en/newsroom.html', 'https://www.marktechpost.com/', 'https://www.nowadais.com/']
# links = []
# for i in urls:
#     links.append( Link( url = i ) )
# load_links( links )
# input( "END..." )


headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}

def get_site_tree( site_link : Link ):
    try:
        response = requests.get( url = site_link.url, headers=headers )

        if response.status_code != 200 and response.status_code != 201:
            raise MessageException( message=f"Error status code - {response.status_code}" )

        response = response.content

        return BeautifulSoup( response, features="lxml" ).find( **site_link.find_kwargs ).text.replace( " ", "" ).replace( "\n", "" ).replace( "\t", "" )
    except:
        if site_link.warning == False:
            site_link.warning = True
        else:
            site_link.is_working = False


def is_changed_site( html_code_first, html_code_second ) -> bool:
    return True if html_code_first != html_code_second else False

def check_site( site_link : Link, a ):
    html_before = get_site_tree( site_link )

    while True:
        if site_link.is_working == False:
            print(f"E1 FOR {site_link.url}")
            return
        
        html_after = get_site_tree( site_link )

        result = is_changed_site( html_code_first=html_before, html_code_second=html_after )

        if result is True:
            print( f"UPDATE IN {site_link.url}" )
            for user_id in user_list:
                bot.send_message( user_id, f"UPDATE FOR {site_link.url}" )

            f = open("txt.txt", "w")
            f.write( f"PART1 - {html_before}\n\n\nPART2 - {html_after}" )
            f.close()
            time.sleep( 10 )

        html_before = html_after

        time.sleep( 0.8 * randint( 1, 3 ) )

def parsing_process( site_urls : list, procces_num : int ) -> None:
    print( f"START PROCCES - {procces_num}" )

    # get start time
    st = time.time()
    
    # Create threads
    thread_list : list[Thread] = []

    for i in range( len( site_urls ) ):
        thread_list.append( Thread( target=check_site, args=( site_urls[i], f"P{procces_num}T{i+1}" ) ) )

    for i in range(len(thread_list)):
        thread_list[i].start()

    for i in range(len(thread_list)):
        thread_list[i].join()

    # get end time
    et = time.time()

    # time between
    print( f"Time for {procces_num} is {et - st}" )





def search_link( url ) -> int:
    for i in range(len(links)):
        if links[i].url == url:
            return i
        
    return None

# @bot.message_handler(content_types=['text'])
# def handler(message):
#     if str(message.from_user.id) not in user_list:
#         bot.send_message( message.from_user.id, "Ошибка доступа" )
#         return

#     if "/add" in message.text:
#         message.text = message.text.replace( "/add ", "" )

#         add_link( Link( message.text ) )

#         bot.send_message( message.from_user.id, "Добавленно." )
#     elif "/del" in message.text:
#         try:
#             message.text = message.text.replace( "/del ", "" )

#             delete_link( search_link(message.text) )

#             bot.send_message( message.from_user.id, "Удаленно." )
#         except:
#             bot.send_message( message.from_user.id, "Ошибка." )
#     elif "/all" in message.text:
#         text = ""

#         for i in range(len(links)):
#             text += f"{i} - {links[i].url} | is working - {links[i].is_working}\n"

#         bot.send_message( message.from_user.id, text )
#     elif "/full" in message.text:
#         message.text = message.text.replace( "/full ", "" )

#         current_link = links[search_link( message.text )]
#         text = f"""URL - {current_link.url}\nIS_WORKING - {int(current_link.is_working)}\nWARNING - {int(current_link.warning)}\n\nFIND_KWARGS - {json.dumps(current_link.find_kwargs)}\n\nWARNING_MESSAGES - {current_link.warning_messages}"""

#         bot.send_message( message.from_user.id, text )
#     elif "/about_link_parameters":
#         text = """URL - Адресс, на который ссылается парсер.\n* При указании адресса, важно сохранять часть 'https://'\n\nIS_WORKING - Говорит, работает ли бот с данной ссылкой\n* Принимает 1 или 0\n\n
# WARNING - При значении True говорит о том, что были полученны какие либо ошибки при работе с данной ссылкой.\n* Если флаг предупреждения активен, то следующий сбой в работе с ссылкой приведет к отключению флага IS_WORKING\n* Принимает 1 или 0\n\n
# FIND_KWARGS - Указывает парсеру, из какого элемента нужно доставать контент, для сравнения.\n* Требуемый формат JSON\n* Поддерживает следующие ключи:\n- name : _имя_тега_\n- attrs : _атрибуты обьекта, такие как класс, айди или любые другие_\n* Формат attrs должен быть так же json\n* По умолчанию указывается { "name" : "body" }\n* Использовать осторожно. Было придуманно, что бы указать боту явный обьект сравнения, что бы избежать сообщений от изменения каких либо динамических обьектов, или не интересующих частей сайта\n\n
# WARNING_MESSAGES - Сообщения о причинах, из-за которых парсер мог заблокировать работу ссылки\n* Что-бы очистить, нужно при изменении параметров ссылки, указать для WARNING_MESSAGES значение []"""
#     elif "/change_link_parameters" in message.text:
#         message.text = message.text.replace( "/change_link_parameters ", "" )

#         url = ""
#         kwargs = ""
#         space_index = 0
#         for i in range(len(message.text)):
#             if message.text[i] != " ":
#                 url += message.text[i]
#             else:
#                 space_index = i
#                 break
#         for i in message.text[ space_index:len(message.text) ]:
#             kwargs += i

#         j : dict = json.loads( kwargs )

#         if j.get( "FIND_KWARGS" ) != None:
#             j[ "FIND_KWARGS" ] = json.loads( j[ "FIND_KWARGS" ] )

#         change_link( search_link( url ), **j )

#         bot.send_message( message.from_user.id, "Параметры изменены" )
#     elif "/help" in message.text:
#         text = """/change_working_status _url_ 0/1 - Если указан 0, то сайт не будет просматриваться парсером, если 1 - будет.\n
# /all - выводит информацию о всех сайтах\n\n/del _url_ - удаляет сайт из парсера\n\n/add _url_ - добавляет сайт в парсер\n\n
# /full _url_ - Выводит полную информацию о указанной ссылке\n\n/about_link_parameters - Даёт информацию о параметрах ссылок\n\n
# /change_link_parameters _url_ _json_ - Изменяет указанную ссылку.\n* В _url_ указывается изменяемая ссылка\n* В _json_ должен передаваться текст соответствующий формату json, состоящий из пары _имя изменяемого параметра_ : _значение_\n* О том какие значения будет корректно указывает читать в  /about_link_parameters\n\n*Любое добавление, удаление, или изменение ссылок в ручную, требует перезапуска парсера"""

#         bot.send_message( message.from_user.id, text )
    



if __name__ == "__main__":
    proc_count = 5

    links = parse_links(  )

    proc_list : list[Process] = []
    urls_index_side = int(len(links) / proc_count)

    for i in range( 1, proc_count + 1 ):
        if i == proc_count:
            proc = Process( target=parsing_process, args=(links[0 + ( urls_index_side * (i - 1) ):-1], i) )
        else:
            proc = Process( target=parsing_process, args=(links[0 + ( urls_index_side * (i - 1) ):( urls_index_side * (i))], i) )

        proc_list.append( proc )

    for proc in proc_list:
        proc.start()


    bot.polling(none_stop=True, interval=0)

