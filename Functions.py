import psycopg2
from telebot import types



def connect():
    conn = psycopg2.connect(dbname='ugzbfpwv', user='ugzbfpwv',
                            password='oaDp4ktCdeDzqUTAmpu-r7MAxLjNjTBk',
                            host='rogue.db.elephantsql.com', port='5432')
    return conn



def info(id, conn):
    there = False
    cursor = conn.cursor()
    sql = "SELECT * FROM clients WHERE id=" + str(id)
    cursor.execute(sql)
    anketa = cursor.fetchall()
    for punct in range(len(anketa[0])-1):
        if anketa[0][1+punct] == "Не заполнено":
            there = True
            return (1+punct)
            break
    if there == False: return "None"


def info2(id, conn):
    there = False
    cursor = conn.cursor()
    sql = "SELECT * FROM work WHERE id=" + str(id)
    cursor.execute(sql)
    anketa = cursor.fetchall()
    for punct in range(len(anketa[0])-1):
        if anketa[0][1+punct] == "Не заполнено":
            there = True
            return (1+punct)
            break
    if there == False: return "None"



def text4(punct, id, conn):
    cursor = conn.cursor()
    sql = "SELECT * FROM work WHERE id=" + str(id)
    cursor.execute(sql)
    result = cursor.fetchall()
    if punct == 1: end = " *НАПИШИТЕ НОМЕР ЗАКАЗА* "
    elif punct == 2: end = " *НАПИШИТЕ *_ПРАВДИВУЮ_* СТОИМОСТЬ ТОВАРА, КОТОРУЮ ВЫ СМОГЛИ НАЙТИ* "
    elif punct == 3: end = " *ВСТАВЬТЕ ССЫЛКИ НА НАЙДЕННЫЕ ВАМИ САЙТЫ И Т.Д.* "
    elif punct == 4: end = " *НАПИШИТЕ СВОЁ СООБЩЕНИЕ ПРОДАВЦУ* "
    else: end = "*Проверьте указанные данные, перед тем, как отправить работу заказчику*\n\n 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n📋 Заказ:  _"\
                         + str(result[0][1]) + "_\n➖\n💲 Ваша сумма:  _" + str(result[0][2]) + "_\n➖\n↗ Ссылки:  _" + str(result[0][3]) + "_\n➖\n✏ Сообщение:  _" + str(result[0][4]) + "_"

    return str(end)


def text5(id, conn):
    sql = "SELECT * FROM made WHERE id=" + str(id)
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    end = "*Ваша выполненная работа*\n\n 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n📋 Заказ:  _"\
                         + str(result[0][1]) + "_\n➖\n💲 Ваша сумма:  _" + str(result[0][2]) + "_\n➖\n↗ Ссылки:  _" + str(result[0][3]) + "_\n➖\n✏ Сообщение:  _" + str(result[0][4]) + "_"

    return str(end)



def text(punct, id, conn):
    cursor = conn.cursor()
    sql = "SELECT * FROM clients WHERE id=" + str(id)
    cursor.execute(sql)
    result = cursor.fetchall()
    if punct == 1: end = " *НАПИШИТЕ КАКОЙ ТОВАР ВЫ ИЩИТЕ* "
    elif punct == 2: end = " *НАПИШИТЕ КОЛИЧЕСТВО НУЖНОГО ТОВАРА* "
    elif punct == 3: end = " *НАПИШИТЕ ИЗВЕСТНУЮ ВАМ ЦЕНУ, ЕСЛИ ЗНАЕТЕ* "
    elif punct == 4: end = " *НАПИШИТЕ ВАШ РЕГИОН* "
    else: end = "*Ваше объявление 📋*\n\n 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🛒 Товар:  _"\
                         + str(result[0][1]) + "_\n➖\n♾ Количество:  _" + str(result[0][2]) + "_\n➖\n💲 Сумма:  _" + str(result[0][3]) + "_\n➖\n🏢 Город:  _" + str(result[0][4]) + "_"

    return str(end)

def text2(id, conn):
    cursor = conn.cursor()
    sql = "SELECT * FROM clients WHERE id=" + str(id)
    cursor.execute(sql)
    result = cursor.fetchall()
    form = "*Ваше объявление 📋*\n\n 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🛒 *Товар*:  _"\
                         + str(result[0][1]) + "_\n➖\n♾ *Количество*:  _" + str(result[0][2]) + "_\n➖\n💲 *Сумма*:  _" + str(result[0][3]) + "_\n➖\n🏢 *Город*:  _" + str(result[0][4]) + "_"
    end = "\n\n 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\n✅ *ВАШЕ ОБЪЯВЛЕНИЕ ГОТОВО* ✅\n"
    return str(form +
               end)

def text3(conn):
    cursor = conn.cursor()
    sql = "SELECT * FROM zakaz"
    cursor.execute(sql)
    res = cursor.fetchall()
    num = len(res)-1
    result = res[num]
    form = "*Новый заказ 📋*\n\n 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n🛒 *Товар*:  _"\
                         + str(result[1]) + "_\n➖\n♾ *Количество*:  _" + str(result[2]) + "_\n➖\n💲 *Сумма*:  _" + str(result[3]) + "_\n➖\n🏢 *Город*:  _" + str(result[4]) + "_"
    end = "\n\n 〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\nℹ *НОМЕР ЗАКАЗА: " + str(num+1) + "*"
    return str(form + end)


def list():
    keys_list = types.KeyboardButton('📃 Список доступных заказов')
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(keys_list)
    return menu


def zakazs(all, id, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zakaz")
    res = cursor.fetchall()
    i = 0
    if all == True:
        message = "*Список заказов:*\n"
        for z in res:
            i += 1
            message += "\n*№" + str(i) + "*  _[Взяло заказ: " + str(z[5]) + "/5, Выполнило: " + str(z[6]) + "/3]_"
    else:
        sql = "SELECT zakaz FROM made WHERE id=" + str(id)
        cursor.execute(sql)
        yet = cursor.fetchall()
        udo = []
        for j in yet:
            if udo.count(j[0]) == 0: udo.append(j[0])
        message = "*Вам доступны заказы с номерами:*\n"
        for z in res:
            i += 1
            if int(z[5]) < 5 and int(z[6]) < 3 and udo.count(i) == 0:
                message += "\n*№" + str(i) + "*  _[Взяло заказ: " + str(z[5]) + "/5, Выполнило: " + str(z[6]) + "/3]_"
    if message=="*Вам доступны заказы с номерами:*\n":
        message = "*У вас нет доступных заказов. Ожидайте, пока появятся новые.*"
    elif message == "*Список заказов:*\n":
        message = "*Заказов пока что нет.*"
    return message


def ready(zakaz, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM made WHERE zakaz=" + str(zakaz))
    res = cursor.fetchall()
    message = "*ВАШ ЗАКАЗ УСПЕШНО ВЫПОЛНИЛИ!*\n\nВот работы трёх наших исполнителей:\n\n"
    i = 0
    for r in res:
        i += 1
        message += "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\nИсполнитель: №" + str(i) + "\nНашёл товар по цене: " + str(r[2]) + "\nСсылки на товар: " + str(r[3]) + "\nСообщение от исполнителя: " + str(r[4]) + "\n"
    message += "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\n_Если какой-то из исполнителей предоставил нерабочие ссылки, или написал совершенно неверную сумму, или обманул вас в чём-то, вы можете подать на него жалобу. Если модератор одобрит жалобу, то старый исполнитель будет наказан, а мы предоставим вам нового._ *Пожалуйста, не подавайте ложных жалоб.*\n\nОжидаем вашего решения. Если в течении 48 часов от вас не будет ответа, заказ одобрится автоматически."
    return message