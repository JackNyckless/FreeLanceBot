import telebot
from telebot import types
import Functions, Config
import SQL
from psycopg2 import sql as sq


token = Config.token
channel = Config.channel_id
admin = Config.admin_id
invite = Config.invite_link


add_ = False
remove_ = False


bot = telebot.TeleBot(token)





def panel(chat):
    a_add = types.InlineKeyboardButton("✅ Добавить исполнителя", callback_data='a_add')
    a_remove = types.InlineKeyboardButton("❌ Исключить исполнителя", callback_data='a_remove')
    a_list = types.InlineKeyboardButton("📃 Список исполнителей", callback_data='a_list')
    a_zakazs = types.InlineKeyboardButton("📋 Список заказов", callback_data='a_zakazs')
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(a_add, a_remove, a_list, a_zakazs)
    bot.send_message(chat, "*АДМИН ПАНЕЛЬ 🔧*", reply_markup=markup, parse_mode="Markdown")






@bot.message_handler(commands=['start'])
def start(message):
    conn = Functions.connect()
    cursor = conn.cursor()
    sql = "SELECT * FROM users WHERE id=" + str(message.from_user.id)
    cursor.execute(sql)
    res = cursor.fetchall()
    if res == []:
        albums = [int(message.from_user.id), None, 1, 0, 0, 0]
        sql = sq.SQL('INSERT INTO users (id, type, anketa, get_result, areason) VALUES ({})').format(
            sq.SQL(',').join(map(sq.Literal, albums)))
        cursor.execute(sql)
    conn.commit()
    conn.close()
    if message.from_user.id == admin:
        bot.send_message(message.chat.id, "_Ваш аккаунт - _*администратор.*", parse_mode="Markdown")
        panel(message.chat.id)
    else:
        customer = types.InlineKeyboardButton("👨‍💼 Я клиент", callback_data='customer')
        executor = types.InlineKeyboardButton("👨‍💻 Я исполнитель", callback_data='executor')
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(customer, executor)
        bot.send_message(message.chat.id, "Привет! 😁\n\n_Хочешь найти товар по_ *доступной цене*, _а главное_ *быстро*_? Тогда наш сервис поможет тебе! " +
                         "Просто оставь своё объявление и трое из наших исполнителей помогут вам с поисками._\n\n✅*Первая заявка бесплатная!*\n✅*Поиск занимает до 2 дней!*\n✅*Обратная связь с администрацией!*",
                         parse_mode="Markdown")
        bot.send_message(message.chat.id, "*Для начала выбери, кто ты?*", reply_markup=markup, parse_mode="Markdown")





@bot.message_handler(content_types=['text'])
def lalala(message):
    global add_, remove_
    conn = Functions.connect()
    cursor = conn.cursor()
    if message.from_user.id != admin:
        sql = "SELECT * FROM workers WHERE id=" + str(message.from_user.id)
        cursor.execute(sql)
        fff = cursor.fetchall()
        sql = "SELECT * FROM users WHERE id=" + str(message.from_user.id)
        cursor.execute(sql)
        rres = cursor.fetchall()
        if message.text == "тест":
            sql = """
                                                                         UPDATE users 
                                                                         SET get_result = 1
                                                                         WHERE id = """ + str(message.from_user.id)
            cursor.execute(sql)
            conn.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            allow = types.InlineKeyboardButton("✅ Одобрить", callback_data='allow')
            deny = types.InlineKeyboardButton("❌ Отклонить", callback_data='deny')
            markup.add(allow, deny)
            res = bot.send_message(message.from_user.id, Functions.ready(1, conn), parse_mode="Markdown",
                                   reply_markup=markup)
            sql = """
                                                                         UPDATE reports 
                                                                         SET mes = """ + str(res.message_id) + """
                                                                         WHERE zakaz = """ + str(1)
            cursor.execute(sql)
            conn.commit()
        elif int(rres[0][4]) != 0:
            sql = """
                UPDATE users
                SET areason = 0 
                WHERE id = """ + str(message.from_user.id)
            cursor.execute(sql)
            sql = """
                            UPDATE reports
                            SET reason = '""" + str(message.text) + """' 
                            WHERE zakaz = """ + str(int(rres[0][4]))
            cursor.execute(sql)
            conn.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            allow = types.InlineKeyboardButton("✅ Одобрить", callback_data='a_allow')
            deny = types.InlineKeyboardButton("❌ Отклонить", callback_data='a_deny')
            markup.add(allow, deny)
            res = bot.send_message(Config.admin_id, Functions.report(conn, int(rres[0][4]), message.from_user.id, message.from_user.username), parse_mode="Markdown", reply_markup=markup)
            bot.send_message(message.chat.id, "*Ваша жалоба успешно отправлена!*\n\nОжидайте пока её рассмотрят.", parse_mode="Markdown")
            sql = """
                                        UPDATE reports 
                                        SET mes = """ + str(res.message_id) + """
                                        WHERE zakaz = """ + str(int(rres[0][4]))
            cursor.execute(sql)
            conn.commit()
        elif fff != []:
            if message.text == "📃 Список доступных заказов":
                bot.send_message(message.chat.id, Functions.zakazs(False, message.from_user.id, conn), parse_mode="Markdown")
            else:
                punct = "None"
                if Functions.info2(message.chat.id, conn) == 1: punct = "zakaz"
                if Functions.info2(message.chat.id, conn) == 2: punct = "summ"
                if Functions.info2(message.chat.id, conn) == 3: punct = "result"
                if Functions.info2(message.chat.id, conn) == 4: punct = "comment"

                if punct == "zakaz":
                    fail = False
                    zn = 0
                    try: zn = int(message.text)
                    except:
                        fail = True
                        bot.send_message(message.chat.id, "*ВЫ ВВЕЛИ НЕКОРЕКТНЫЙ НОМЕР!*\n\nВведите правильный номер.",
                                         parse_mode="Markdown")
                    if zn != 0:
                        cursor.execute("SELECT * FROM zakaz")
                        kz = len(cursor.fetchall())
                        if zn > 0 and zn < kz + 1:
                            sql = "SELECT * FROM made WHERE id="+str(message.from_user.id)+" AND zakaz=" + message.text
                            cursor.execute(sql)
                            yet = cursor.fetchall()
                            sql = "SELECT * FROM zakaz"
                            cursor.execute(sql)
                            res_ = cursor.fetchall()[0]
                            id = int(res_[0])
                            tkers = int(res_[5])
                            endrs =int(res_[6])
                            conn.commit()
                            if yet != []:
                                bot.send_message(message.chat.id,
                                                 "*ВЫ УЖЕ ВЫПОЛНИЛИ ЭТОТ ЗАКАЗ!*\n\nВозьмите другой заказ.",
                                                 parse_mode="Markdown")
                            elif endrs > 2:
                                bot.send_message(message.chat.id,
                                                 "*ЭТОТ ЗАКАЗ УЖЕ ВЫПОЛНИЛИ!*\n\nВозьмите другой заказ.",
                                                 parse_mode="Markdown")
                            elif tkers > 4:
                                bot.send_message(message.chat.id,
                                                 "*ЭТОТ ЗАКАЗ ВЗЯЛО СЛИШКОМ МНОГО ИСПОЛНИТЕЛЕЙ*\n\nВозьмите другой заказ.",
                                                 parse_mode="Markdown")
                            else:
                                sql = """
                                                                             UPDATE zakaz 
                                                                             SET takers = """ + str(tkers + 1) + """
                                                                             WHERE id = """ + str(id)
                                cursor.execute(sql)
                                conn.commit()
                                if punct != "None":
                                    sql = """
                                                    UPDATE work 
                                                    SET """ + punct + """ = '""" + str(message.text) + """' 
                                                    WHERE id = """ + str(message.from_user.id)

                                    cursor.execute(sql)
                                    conn.commit()
                                markup = types.InlineKeyboardMarkup(row_width=2)
                                if Functions.info2(message.from_user.id, conn) == "None":
                                    zakaz = types.InlineKeyboardButton("📝 Изменить НОМЕР ЗАКАЗА", callback_data='zakaz')
                                    summ = types.InlineKeyboardButton("📝 Изменить СУММУ", callback_data='summ')
                                    result = types.InlineKeyboardButton("📝 Изменить ССЫЛКИ", callback_data='result')
                                    comment = types.InlineKeyboardButton("📝 Изменить СООБЩЕНИЕ", callback_data="comment")
                                    enter2 = types.InlineKeyboardButton("📬 Отправить на проверку", callback_data="enter2")
                                    clear2 = types.InlineKeyboardButton("🗑 Очистить", callback_data="clear2")

                                    sql = "SELECT * FROM work WHERE id=" + str(message.from_user.id)
                                    cursor.execute(sql)
                                    anketa = cursor.fetchall()

                                    markup.add(clear2)

                                    buttons = []
                                    for punct in range(len(anketa[0]) - 1):
                                        if anketa[0][1 + punct] != "Не заполнено":
                                            if punct == 0: buttons.append(zakaz)
                                            if punct == 1: buttons.append(summ)
                                            if punct == 2: buttons.append(result)
                                            if punct == 3: buttons.append(comment)

                                    k = 0
                                    if len(buttons) == 4: k = 5

                                    while buttons != []:
                                        if len(buttons) > 1:
                                            markup.add(buttons[0], buttons[1])
                                            buttons.remove(buttons[1])
                                            buttons.remove(buttons[0])
                                        else:
                                            markup.add(buttons[0])
                                            buttons.remove(buttons[0])

                                    if k == 5: markup.add(enter2)

                                conn.commit()
                                bot.send_message(message.chat.id, Functions.text4(Functions.info2(message.chat.id, conn), message.from_user.id, conn),
                                                 reply_markup=markup, parse_mode="Markdown")
                        else:
                            bot.send_message(message.chat.id, "*ЗАКАЗА С ТАКИМ НОМЕРОМ НЕ СУЩЕСТВУЕТ!*\n\nВведите правильный номер.",
                                             parse_mode="Markdown")
                    elif zn == 0 and fail == False:
                        bot.send_message(message.chat.id,
                                         "*НОМЕР ЗАКАЗА НЕ МОЖЕТ БЫТЬ НУЛЕВЫМ!*\n\nВведите правильный номер.",
                                         parse_mode="Markdown")
                else:
                    if punct != "None":
                        sql = """
                                            UPDATE work
                                            SET """ + punct + """ = '""" + str(message.text) + """' 
                                            WHERE id = """ + str(message.from_user.id)

                        cursor.execute(sql)
                        conn.commit()
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    if Functions.info2(message.from_user.id, conn) == "None":
                        zakaz = types.InlineKeyboardButton("📝 Изменить НОМЕР ЗАКАЗА", callback_data='zakaz')
                        summ = types.InlineKeyboardButton("📝 Изменить СУММУ", callback_data='summ')
                        result = types.InlineKeyboardButton("📝 Изменить ССЫЛКИ", callback_data='result')
                        comment = types.InlineKeyboardButton("📝 Изменить СООБЩЕНИЕ", callback_data="comment")
                        enter2 = types.InlineKeyboardButton("📬 Отправить на проверку", callback_data="enter2")
                        clear2 = types.InlineKeyboardButton("🗑 Очистить", callback_data="clear2")

                        sql = "SELECT * FROM work WHERE id=" + str(message.from_user.id)
                        cursor.execute(sql)
                        anketa = cursor.fetchall()

                        markup.add(clear2)

                        buttons = []
                        for punct in range(len(anketa[0]) - 1):
                            if anketa[0][1 + punct] != "Не заполнено":
                                if punct == 0: buttons.append(zakaz)
                                if punct == 1: buttons.append(summ)
                                if punct == 2: buttons.append(result)
                                if punct == 3: buttons.append(comment)

                        k = 0
                        if len(buttons) == 4: k = 5

                        while buttons != []:
                            if len(buttons) > 1:
                                markup.add(buttons[0], buttons[1])
                                buttons.remove(buttons[1])
                                buttons.remove(buttons[0])
                            else:
                                markup.add(buttons[0])
                                buttons.remove(buttons[0])

                        if k == 5: markup.add(enter2)

                    conn.commit()
                    bot.send_message(message.chat.id, Functions.text4(Functions.info2(message.chat.id, conn), message.from_user.id, conn),
                                     reply_markup=markup, parse_mode="Markdown")
        else:
            sql = "SELECT * FROM clients WHERE id=" + str(message.from_user.id)
            cursor.execute(sql)
            res = cursor.fetchall()
            sql = "SELECT * FROM users WHERE id=" + str(message.from_user.id)
            cursor.execute(sql)
            res2 = cursor.fetchall()
            if res == []:
                bot.send_message(message.chat.id, "*Прочитай информацию выше!*",
                                 parse_mode="Markdown")
            elif res2[0][2] == 0:
                bot.send_message(message.chat.id, "*Оплатите, чтобы создать ещё одно объявление.*",
                                 parse_mode="Markdown")
            else:
                punct = "None"
                if Functions.info(message.chat.id, conn) == 1: punct = "name"
                if Functions.info(message.chat.id, conn) == 2: punct = "count"
                if Functions.info(message.chat.id, conn) == 3: punct = "summ"
                if Functions.info(message.chat.id, conn) == 4: punct = "city"

                if punct != "None":

                    sql = """
                        UPDATE clients 
                        SET """ + punct + """ = '""" + str(message.text) + """' 
                        WHERE id = """ + str(message.from_user.id)

                    cursor.execute(sql)
                    conn.commit()
                markup = types.InlineKeyboardMarkup(row_width=2)
                if Functions.info(message.from_user.id, conn) == "None":
                    name = types.InlineKeyboardButton("📝 Изменить ТОВАР", callback_data='name')
                    count = types.InlineKeyboardButton("📝 Изменить КОЛИЧЕСТВО", callback_data='count')
                    summ = types.InlineKeyboardButton("📝 Изменить СУММУ", callback_data='summ')
                    city = types.InlineKeyboardButton("📝 Изменить ГОРОД", callback_data="city")
                    enter = types.InlineKeyboardButton("📬 Отправить объявление", callback_data="enter")
                    clear = types.InlineKeyboardButton("🗑 Очистить", callback_data="clear")


                    sql = "SELECT * FROM clients WHERE id=" + str(message.from_user.id)
                    cursor.execute(sql)
                    anketa = cursor.fetchall()

                    markup.add(clear)

                    buttons = []
                    for punct in range(len(anketa[0]) - 1):
                        if anketa[0][1 + punct] != "Не заполнено":
                            if punct == 0: buttons.append(name)
                            if punct == 1: buttons.append(count)
                            if punct == 2: buttons.append(summ)
                            if punct == 3: buttons.append(city)


                    k = 0
                    if len(buttons) == 4: k = 5

                    while buttons != []:
                        if len(buttons) > 1:
                            markup.add(buttons[0], buttons[1])
                            buttons.remove(buttons[1])
                            buttons.remove(buttons[0])
                        else:
                            markup.add(buttons[0])
                            buttons.remove(buttons[0])

                    if k == 5: markup.add(enter)

                conn.commit()
                bot.send_message(message.chat.id, Functions.text(Functions.info(message.chat.id, conn), message.from_user.id, conn),
                                       reply_markup=markup, parse_mode="Markdown")

    else:
        sql = "SELECT * FROM users"
        cursor.execute(sql)
        users = cursor.fetchall()
        user = []
        for u in users:
            if u[5] != 0:
                user = u
                break
        if user != []:
            sql = """
                            UPDATE users 
                            SET a_deny = 0
                            WHERE id = """ + str(message.from_user.id)

            cursor.execute(sql)
            conn.commit()
            bot.send_message(message.chat.id,
                             "*Вы отклонили жалобу в заказке №" + str(user[5]) + "*\n\nВаше пояснение: '_" + str(message.text) + "_'",
                             parse_mode="Markdown")
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            zakazs = cursor.fetchall()
            nid = int(zakazs[user[5]-1][0])
            bot.send_message(nid,
                             "*Вашу жалобу к заказу №" + str(user[5]) + " отклонили!*\n\nСообщение модератора: '_" + str(
                                 message.text) + "_'",
                             parse_mode="Markdown")
        elif add_ == True:
            try:
                id = int(message.text)
                sql = "SELECT * FROM users WHERE id=" + str(id)
                cursor.execute(sql)
                res = cursor.fetchall()
                if res == []:
                    bot.send_message(message.chat.id, "*Данный пользователь ещё не запускал бота.\n\nСкажите ему, чтобы сделал это!*",
                                     parse_mode="Markdown")
                else:
                    sql = "SELECT * FROM workers WHERE id=" + str(id)
                    cursor.execute(sql)
                    if cursor.fetchall() != []:
                        bot.send_message(message.chat.id, "*Данный пользователь уже является исполнителем!*",
                                         parse_mode="Markdown")
                    else:
                        albums = [id, 0, 0, 0]
                        sql = sq.SQL('INSERT INTO workers (id, balance, zakas, warns) VALUES ({})').format(
                            sq.SQL(',').join(map(sq.Literal, albums)))
                        cursor.execute(sql)
                        conn.commit()
                        bot.unban_chat_member(channel, id)
                        albums = [id, "Не заполнено", "Не заполнено", "Не заполнено", "Не заполнено"]
                        sql = sq.SQL('INSERT INTO work (id, zakaz, summ, result, comment) VALUES ({})').format(
                            sq.SQL(',').join(map(sq.Literal, albums)))
                        cursor.execute(sql)
                        conn.commit()
                        bot.send_message(id, "*✅ Вас приняли в команду исполнителей!*\n\n_Наш канал с заказами, переходи скорее:_\n" + invite, parse_mode="Markdown", reply_markup=Functions.list())
                        bot.send_message(id, "*ЧТОБЫ ВЫПОЛНИТЬ ЗАКАЗ, НАПИШИТЕ МНЕ ЕГО НОМЕР*", parse_mode="Markdown")
                        bot.send_message(message.chat.id, "*Пользователь успешно добавлен в команду исполнителей!*",
                                         parse_mode="Markdown")
            except:
                bot.send_message(message.chat.id, "*Вы отменили команду или ввели некоректное значение.*", parse_mode="Markdown")
            add_ = False
            panel(message.chat.id)
        elif remove_ == True:
            try:
                id = int(message.text)
                sql = "SELECT * FROM workers WHERE id=" + str(id)
                cursor.execute(sql)
                if cursor.fetchall() == []:
                    bot.send_message(message.chat.id, "*Исполнителя с таким id нет.*",
                                     parse_mode="Markdown")
                else:
                    sql = "DELETE FROM workers WHERE id=" + str(id)
                    cursor.execute(sql)
                    conn.commit()
                    bot.kick_chat_member(channel, id)
                    sql = "DELETE FROM work WHERE id=" + str(id)
                    cursor.execute(sql)
                    conn.commit()
                    bot.send_message(id,
                                     "*❌ Вас исключили из команды исполнителей!*\n\n_Нам очень жаль._",
                                     parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
                    bot.send_message(message.chat.id, "*Пользователь успешно исключён из команды исполнителей!*",
                                     parse_mode="Markdown")
            except:
                bot.send_message(message.chat.id, "*Вы отменили команду или ввели некоректное значение.*", parse_mode="Markdown")
            add_ = False
            panel(message.chat.id)
        else:
            bot.send_message(message.chat.id, "*Выбери команду с помощью кнопок.*",
                             parse_mode="Markdown")

    conn.close()


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global add_, remove_
    conn = Functions.connect()
    cursor = conn.cursor()
    cid = call.from_user.id
    if cid != admin:
        if call.data == "customer" or call.data == "executor":
            if call.data == "customer":
                sql = "SELECT * FROM clients WHERE id=" + str(cid)
                cursor.execute(sql)
                check = cursor.fetchall()
                if check == []:
                    albums = [int(cid), "Не заполнено", "Не заполнено", "Не заполнено", "Не заполнено"]
                    sql = sq.SQL('INSERT INTO clients (id, name, count, summ, city) VALUES ({})').format(
                        sq.SQL(',').join(map(sq.Literal, albums)))
                    cursor.execute(sql)
                conn.commit()
                sql = """
                    UPDATE users
                    SET type = 'заказчик' 
                    WHERE id = """ + str(cid)
                cursor.execute(sql)
                conn.commit()
                bot.send_message(call.message.chat.id, "*Отлично!* Теперь заполните объявление, отвечая на вопросы!", parse_mode="Markdown")
                bot.send_message(call.message.chat.id, Functions.text(Functions.info(cid, conn), cid, conn), parse_mode="Markdown")
            if call.data == "executor":
                sql = """
                    UPDATE users 
                    SET type = 'исполнитель' 
                    WHERE id = """ + str(cid)
                cursor.execute(sql)
                conn.commit()
                bot.send_message(call.message.chat.id, "*Отлично!* _Тогда просим отписаться данному человеку:_\n\n*" + str(bot.get_chat_member(Config.channel_id, Config.admin_id).user.first_name) + " - " + str(Config.admin_link) + "*\n\n*Обязательно напишите ему ваш id!*\n_Ваш id:_ " + str(cid), parse_mode="Markdown")
            bot.delete_message(call.message.chat.id, call.message.message_id)
        elif call.data == "new":
            sql = "SELECT * FROM zakaz WHERE id=" + str(cid)
            cursor.execute(sql)
            if len(cursor.fetchall()) == 1:
                bot.send_message(call.message.chat.id, "‼️*Вы потратили свою бесплатную попытку.*\n\nЧтобы сделать более 1 объявления, оплатите новое или купите подписку на неделю.\n\n_В доработке..._", parse_mode="Markdown")
            else:
                bot.send_message(call.message.chat.id, "_В доработке_", parse_mode="Markdown")
        elif call.data == "allow":
            sql = """
                                                       UPDATE users 
                                                       SET get_result = 0
                                                       WHERE id = """ + str(cid)
            cursor.execute(sql)
            conn.commit()
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "*Вы приняли работу исполнителей!*\n\nНадеемся, вам всё понравилось.", parse_mode="Markdown")
        elif call.data == "deny":
            markup = types.InlineKeyboardMarkup(row_width=1)
            allow = types.InlineKeyboardButton("❗ Подать жалобу на исполнителя", callback_data='report')
            deny = types.InlineKeyboardButton("❓ Другая причина отказа", callback_data='question')
            back = types.InlineKeyboardButton("Назад", callback_data='back')
            markup.add(allow, deny, back)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        elif call.data == "report":
            markup = types.InlineKeyboardMarkup(row_width=3)
            aa = types.InlineKeyboardButton("Исполнитель №1", callback_data='ispoln1')
            aaa = types.InlineKeyboardButton("Исполнитель №2", callback_data='ispoln2')
            aaaa = types.InlineKeyboardButton("Исполнитель №3", callback_data='ispoln3')
            back2 = types.InlineKeyboardButton("Назад", callback_data='back2')
            markup.add(aa, aaa, aaaa, back2)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        elif "reass" in call.data:
            reason = ""
            for ll in call.message.json['reply_markup']['inline_keyboard']:
                for lll in ll:
                    if lll['callback_data'] == call.data:
                        reason = str(lll['text'])
            sql = "SELECT * FROM reports WHERE mes=" + str(call.message.message_id)
            cursor.execute(sql)
            res1 = cursor.fetchall()
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            res2 = cursor.fetchall()
            for r1 in res1:
                i = 0
                for r2 in res2:
                    i += 1
                    if r1[1] == i and r2[0] == cid:
                        break
            sql = """
                            UPDATE reports
                            SET reason = '""" + str(reason) + """' 
                            WHERE zakaz = """ + str(i)
            cursor.execute(sql)
            conn.commit()
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            markup = types.InlineKeyboardMarkup(row_width=2)
            allow = types.InlineKeyboardButton("✅ Одобрить", callback_data='a_allow')
            deny = types.InlineKeyboardButton("❌ Отклонить", callback_data='a_deny')
            markup.add(allow, deny)
            res = bot.send_message(Config.admin_id, Functions.report(conn, i, cid, call.from_user.username), parse_mode="Markdown", reply_markup=markup)
            bot.send_message(call.message.chat.id, "*Ваша жалоба успешно отправлена!*\n\nОжидайте пока её рассмотрят.",
                             parse_mode="Markdown")
            sql = """
                                        UPDATE reports 
                                        SET mes = """ + str(res.message_id) + """
                                        WHERE zakaz = """ + str(i)
            cursor.execute(sql)
            conn.commit()
        elif "ispoln" in call.data:
            cmd = str(call.data)
            n = int(cmd.replace("ispoln",""))
            sql = "SELECT * FROM reports WHERE mes=" + str(call.message.message_id)
            cursor.execute(sql)
            res1 = cursor.fetchall()
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            res2 = cursor.fetchall()
            for r1 in res1:
                i = 0
                for r2 in res2:
                    i += 1
                    if r1[1] == i and r2[0] == cid:
                        break
            sql = "SELECT * FROM made WHERE zakaz=" + str(i)
            cursor.execute(sql)
            res3 = cursor.fetchall()
            who = res3[n-1][0]
            sql = """
                UPDATE reports
                SET who = """ + str(who) + """ 
                WHERE zakaz = """ + str(i)
            cursor.execute(sql)
            conn.commit()
            markup = types.InlineKeyboardMarkup(row_width=2)
            rsum = types.InlineKeyboardButton("Некоректная сумма", callback_data='reasssum')
            rlink = types.InlineKeyboardButton("Нерабочие ссылки", callback_data='reasslink')
            rmes = types.InlineKeyboardButton("Бред в сообщении", callback_data='reassmes')
            rall = types.InlineKeyboardButton("Заказ не выполнен", callback_data='reassall')
            back3 = types.InlineKeyboardButton("Назад", callback_data='back3')
            markup.add(rsum, rlink, rmes, rall, back3)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        elif call.data == "back3":
            sql = "SELECT * FROM reports WHERE mes=" + str(call.message.message_id)
            cursor.execute(sql)
            res1 = cursor.fetchall()
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            res2 = cursor.fetchall()
            for r1 in res1:
                i = 0
                for r2 in res2:
                    i += 1
                    if r1[1] == i and r2[0] == cid:
                        break
            sql = """
                            UPDATE reports
                            SET who = 0
                            WHERE zakaz = """ + str(i)
            cursor.execute(sql)
            conn.commit()
            markup = types.InlineKeyboardMarkup(row_width=3)
            aa = types.InlineKeyboardButton("Исполнитель №1", callback_data='ispoln1')
            aaa = types.InlineKeyboardButton("Исполнитель №2", callback_data='ispoln2')
            aaaa = types.InlineKeyboardButton("Исполнитель №3", callback_data='ispoln3')
            back2 = types.InlineKeyboardButton("Назад", callback_data='back2')
            markup.add(aa, aaa, aaaa, back2)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        elif call.data == "question":
            sql = "SELECT * FROM reports WHERE mes=" + str(call.message.message_id)
            cursor.execute(sql)
            num = cursor.fetchall()[0][0]
            sql = """
                UPDATE users
                SET areason = """ + str(num) + """ 
                WHERE id = """ + str(cid)
            cursor.execute(sql)
            conn.commit()
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "*Напишите свою причину.*\n\n_Как можно понятнее!_", parse_mode="Markdown")
        elif call.data == "back":
            markup = types.InlineKeyboardMarkup(row_width=2)
            allow = types.InlineKeyboardButton("✅ Одобрить", callback_data='allow')
            deny = types.InlineKeyboardButton("❌ Отклонить", callback_data='deny')
            markup.add(allow, deny)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        elif call.data == "back2":
            markup = types.InlineKeyboardMarkup(row_width=1)
            allow = types.InlineKeyboardButton("❗ Подать жалобу на исполнителя", callback_data='report')
            deny = types.InlineKeyboardButton("❓ Другая причина отказа", callback_data='question')
            back = types.InlineKeyboardButton("Назад", callback_data='back')
            markup.add(allow, deny, back)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        elif call.data == "enter" or call.data == "enter2":
            sql = "SELECT * FROM workers WHERE id=" + str(cid)
            cursor.execute(sql)
            if cursor.fetchall() != [] and call.data == "enter2":
                sql = "SELECT * FROM work WHERE id=" + str(cid)
                cursor.execute(sql)
                albums = cursor.fetchall()[0]
                albums2 = []
                for i in range(5):
                    albums2.append(albums[i])
                for i in range(2):
                    albums2.append(False)
                sql = """
                                                        UPDATE work 
                                                        SET zakaz = 'Не заполнено',
                                                        summ = 'Не заполнено', 
                                                        result = 'Не заполнено', 
                                                        comment = 'Не заполнено' 
                                                        WHERE id = """ + str(cid)

                cursor.execute(sql)
                conn.commit()
                sql = sq.SQL('INSERT INTO made (id, zakaz, summ, result, comment, truth, agree) VALUES ({})').format(
                    sq.SQL(',').join(map(sq.Literal, albums2)))
                cursor.execute(sql)
                conn.commit()
                sql = "SELECT * FROM zakaz"
                cursor.execute(sql)
                res_ = cursor.fetchall()[int(albums2[1]) - 1]
                id = int(res_[0])
                endrs = int(res_[6])
                sql = """
                                                         UPDATE zakaz 
                                                         SET enders = """+str(endrs+1)+"""
                                                         WHERE id = """ + str(id)
                cursor.execute(sql)
                conn.commit()
                bot.send_message(id, "*Ваш заказ выполнил один из наших исполнителей.*", parse_mode="Markdown")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=Functions.text5(cid, conn), parse_mode="Markdown")
                bot.send_message(call.message.chat.id,
                                 "*Вы успешно выполнили заказ! Теперь ожидайте, пока его выполнение подтвердит сам заказчик. Мы уведомим вас.*\n\nВы пока можете перейти к выполнению следующего заказа.",
                                 parse_mode="Markdown")
                bot.send_message(call.message.chat.id, "*НАПИШИТЕ НОМЕР ЗАКАЗА, КОТОРЫЙ ХОТИТЕ ВЫПОЛНИТЬ*", parse_mode="Markdown")
                if endrs+1 == 3:
                    sql = """
                                                             UPDATE users 
                                                             SET get_result = 1
                                                             WHERE id = """ + str(id)
                    cursor.execute(sql)
                    conn.commit()
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    allow = types.InlineKeyboardButton("✅ Одобрить", callback_data='allow')
                    deny = types.InlineKeyboardButton("❌ Отклонить", callback_data='deny')
                    markup.add(allow, deny)
                    res = bot.send_message(id, Functions.ready(int(albums2[1]), conn), parse_mode="Markdown", reply_markup=markup)
                    print(res.message_id)
                    sql = """
                                                             UPDATE reports 
                                                             SET mes = """ + str(res.message_id) + """
                                                             WHERE zakaz = """ + str(int(albums2[1]))
                    cursor.execute(sql)
                    conn.commit()

            elif call.data == "enter":
                sql = "SELECT * FROM users WHERE id=" + str(cid)
                cursor.execute(sql)
                res2 = cursor.fetchall()
                if res2 != []:
                    if res2[0][2] == 0:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=Functions.text(Functions.info(cid, conn), cid, conn), parse_mode="Markdown")
                    else:
                        sql = "SELECT * FROM clients WHERE id=" + str(cid)
                        cursor.execute(sql)
                        albums = cursor.fetchall()[0]
                        albums2 = []
                        for i in range(5):
                            albums2.append(albums[i])
                        for i in range(2):
                            albums2.append("0")
                        sql = """
                                                UPDATE clients
                                                SET name = 'Не заполнено',
                                                count = 'Не заполнено', 
                                                summ = 'Не заполнено', 
                                                city = 'Не заполнено' 
                                                WHERE id = """ + str(cid)

                        cursor.execute(sql)
                        conn.commit()
                        sql = sq.SQL(
                            'INSERT INTO zakaz (id, name, count, summ, city, takers, enders) VALUES ({})').format(
                            sq.SQL(',').join(map(sq.Literal, albums2)))
                        cursor.execute(sql)
                        conn.commit()
                        sql = """
                            UPDATE users
                            SET anketa = 0
                            WHERE id =""" + str(cid)
                        cursor.execute(sql)
                        conn.commit()
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        new = types.InlineKeyboardButton("✳ Создать новое", callback_data="new")
                        markup.add(new)
                        bot.send_message(channel, Functions.text3(conn), parse_mode="Markdown")
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=Functions.text2(cid, conn), parse_mode="Markdown")
                        bot.send_message(call.message.chat.id, "*Исполнители получили вашу заявку. Ожидайте, скоро мы пришлём вам результат работы.*\n\n_Если хотите создать ещё одно объявление, нажмите на кнопку._", reply_markup=markup, parse_mode="Markdown")
        else:
            sql = "SELECT * FROM workers WHERE id=" + str(cid)
            cursor.execute(sql)
            if cursor.fetchall() != []:
                try:
                    if call.data == "clear2":
                        sql = """
                                                UPDATE work
                                                SET zakaz = 'Не заполнено',
                                                summ = 'Не заполнено', 
                                                result = 'Не заполнено', 
                                                comment = 'Не заполнено' 
                                                WHERE id = """ + str(cid)

                        cursor.execute(sql)
                        conn.commit()
                    else:
                        sql = """
                                    UPDATE work
                                    SET """ + str(call.data) + """ = 'Не заполнено' 
                                    WHERE id = """ + str(cid)

                        cursor.execute(sql)
                        conn.commit()

                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=Functions.text4(Functions.info2(cid, conn), cid, conn), parse_mode="Markdown")
                except:
                    exc = True


            else:
                try:
                    if call.data == "clear":
                        sql = """
                                                UPDATE clients
                                                SET name = 'Не заполнено',
                                                count = 'Не заполнено', 
                                                summ = 'Не заполнено', 
                                                city = 'Не заполнено' 
                                                WHERE id = """ + str(cid)

                        cursor.execute(sql)
                        conn.commit()
                    else:
                        sql = """
                                    UPDATE clients 
                                    SET """ + str(call.data) + """ = 'Не заполнено' 
                                    WHERE id = """ + str(cid)

                        cursor.execute(sql)
                        conn.commit()


                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=Functions.text(Functions.info(cid, conn), cid, conn), parse_mode="Markdown")
                except:
                    exc = True

    else:
        if call.data == "a_list":
            sql = "SELECT * FROM workers"
            cursor.execute(sql)
            list = cursor.fetchall()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы выбрали: _Список исполнителей_ 📃", parse_mode="Markdown")
            if list == []:
                bot.send_message(call.message.chat.id, "*У вас нет ни одного исполнителя.*", parse_mode="Markdown")
            else:
                mes = "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️"
                for worker in list:
                    mes += "\nid: *" + str(worker[0]) + "*"
                    mes += "\nБаланс: " + str(worker[1])
                    mes += "\nКол-во заказов: " + str(worker[2])
                    mes += "\nПредупреждения: " + str(worker[3])
                    mes += "\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️"
                bot.send_message(call.message.chat.id, mes, parse_mode="Markdown")
            panel(call.message.chat.id)
        if call.data == "a_add":
            add_ = True
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы выбрали: _Добавить исполнителя_ ✅", parse_mode="Markdown")
            bot.send_message(call.message.chat.id, "*Напишите id нового исполнителя.*\n\nНапишите что-нибудь другое, чтобы отменить команду.", parse_mode="Markdown")
        if call.data == "a_remove":
            remove_ = True
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы выбрали: _Исключить исполнителя_ ❌", parse_mode="Markdown")
            bot.send_message(call.message.chat.id, "*Напишите id исключаемого исполнителя.*\n\nНапишите что-нибудь другое, чтобы отменить команду.",
                             parse_mode="Markdown")
        if call.data == "a_zakazs":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы выбрали: _Список заказов_ 📋", parse_mode="Markdown")
            bot.send_message(call.message.chat.id, Functions.zakazs(True, 0, conn), parse_mode="Markdown")
            panel(call.message.chat.id)
        if call.data == "yeswarn":
            sql = "SELECT * FROM reports WHERE mes=" + str(call.message.message_id)
            cursor.execute(sql)
            r1 = cursor.fetchall()[0]
            who = int(r1[2])
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            res2 = cursor.fetchall()
            i = 0
            id = 0
            for r2 in res2:
                i += 1
                if r1[0] == i:
                    id = r2[0]
                    break
            sql = "SELECT * FROM workers WHERE id=" + str(who)
            cursor.execute(sql)
            aa = cursor.fetchall()[0]
            warns = int(aa[3])
            sql = "DELETE FROM made WHERE id=" + str(who) + " AND zakaz=" + str(i)
            cursor.execute(sql)
            conn.commit()
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            res_ = cursor.fetchall()[i-1]
            endrs = int(res_[6])
            tkers = int(res_[5])
            idid = int(res_[0])
            sql = """
                                                                     UPDATE zakaz 
                                                                     SET enders = """ + str(endrs - 1) + """
                                                                     WHERE id = """ + str(idid)
            cursor.execute(sql)
            sql = """
                                                                     UPDATE zakaz 
                                                                     SET takers = """ + str(tkers - 1) + """
                                                                     WHERE id = """ + str(idid)
            cursor.execute(sql)
            conn.commit()
            Functions.update("workers","warns",str(warns+1),"id", str(who))
            bot.send_message(id,
                             "*Вам одобрили жалобу заказа №" + str(i) + "*\n\nИсполнитель получил наказание!\nТакже вам была выдана замена в виде другого исполнителя. Ожидайте его работу.",
                             parse_mode="Markdown")
            bot.send_message(call.message.chat.id, "*Вы одобрили жалобу заказа №" + str(i) + "*\n\nid" + str(who) + " получил наказание!", parse_mode="Markdown")
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == "notwarn":
            sql = "SELECT * FROM reports WHERE mes=" + str(call.message.message_id)
            cursor.execute(sql)
            r1 = cursor.fetchall()[0]
            who = int(r1[2])
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            res2 = cursor.fetchall()
            i = 0
            id = 0
            for r2 in res2:
                i += 1
                if r1[0] == i:
                    id = r2[0]
                    break
            sql = "DELETE FROM made WHERE id=" + str(who) + " AND zakaz=" + str(i)
            cursor.execute(sql)
            conn.commit()
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            res_ = cursor.fetchall()[i - 1]
            endrs = int(res_[6])
            tkers = int(res_[5])
            idid = int(res_[0])
            sql = """
                                                                                 UPDATE zakaz 
                                                                                 SET enders = """ + str(endrs - 1) + """
                                                                                 WHERE id = """ + str(idid)
            cursor.execute(sql)
            sql = """
                                                                                 UPDATE zakaz 
                                                                                 SET takers = """ + str(tkers - 1) + """
                                                                                 WHERE id = """ + str(idid)
            cursor.execute(sql)
            conn.commit()
            bot.send_message(id,
                             "*Вам одобрили жалобу заказа №" + str(
                                 i) + "*\n\nВам была выдана замена в виде другого исполнителя. Ожидайте его работу.",
                             parse_mode="Markdown")
            bot.send_message(call.message.chat.id,
                             "*Вы одобрили жалобу заказа №" + str(i) + "*\n\nid" + str(who) + " не получил наказание!",
                             parse_mode="Markdown")
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data == "a_allow":
            sql = "SELECT * FROM reports WHERE mes=" + str(call.message.message_id)
            cursor.execute(sql)
            if int(cursor.fetchall()[0][2]) == 0:
                bot.send_message(call.message.chat.id, "Ещё недоступно, т.к. не указано, на кого написана жалоба")
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                da = types.InlineKeyboardButton("Выдать наказание исполн.", callback_data="yeswarn")
                net = types.InlineKeyboardButton("Сделать предупреждение исполн.", callback_data="notwarn")
                back = types.InlineKeyboardButton("Назад", callback_data="a_back")
                markup.add(da, net, back)
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        if call.data == "a_deny":
            sql = "SELECT * FROM reports WHERE mes=" + str(call.message.message_id)
            cursor.execute(sql)
            r1 = cursor.fetchall()[0]
            sql = "SELECT * FROM zakaz"
            cursor.execute(sql)
            res2 = cursor.fetchall()
            i = 0
            for r2 in res2:
                i += 1
                if r1[0] == i:
                    break
            sql = """
                            UPDATE users 
                            SET a_deny = """ + str(i) + """
                            WHERE id = """ + str(cid)

            cursor.execute(sql)
            conn.commit()
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(call.message.chat.id, "*Напишите пояснение, почему вы отклонили данную жалобу*", parse_mode="Markdown")
        if call.data == "a_back":
            markup = types.InlineKeyboardMarkup(row_width=2)
            allow = types.InlineKeyboardButton("✅ Одобрить", callback_data='a_allow')
            deny = types.InlineKeyboardButton("❌ Отклонить", callback_data='a_deny')
            markup.add(allow, deny)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markup)

    conn.close()





print("Bot start")
bot.polling(none_stop=True, timeout=123)
