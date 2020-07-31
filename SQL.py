import psycopg2
import Functions




conn = Functions.connect()


cursor = conn.cursor()


try:
    cursor.execute("""CREATE TABLE reports
                  (zakaz INTEGER, mes INTEGER, who INTEGER, reason TEXT)
               """)
except:
    exc = True


conn.commit()


try:
    cursor.execute("""CREATE TABLE users
                  (id INTEGER, type TEXT, anketa INTEGER, get_result INTEGER, areason INTEGER, a_deny INTEGER)
               """)
except:
    exc = True


conn.commit()


try:
    cursor.execute("""CREATE TABLE clients
                  (id INTEGER, name TEXT, count TEXT, summ TEXT, city TEXT)
               """)
except:
    exc = True

conn.commit()


try:
    cursor.execute("""CREATE TABLE work
                  (id INTEGER, zakaz TEXT, summ TEXT, result TEXT, comment TEXT)
               """)
except:
    exc = True

conn.commit()


try:
    cursor.execute("""CREATE TABLE workers
                  (id INTEGER, balance INTEGER, zakas INTEGER, warns INTEGER)
               """)
except:
    exc = True

conn.commit()



try:
    cursor.execute("""CREATE TABLE zakaz
                  (id INTEGER, name TEXT, count TEXT, summ TEXT, city TEXT, takers TEXT, enders TEXT)
               """)
except:
    exc = True


conn.commit()



try:
    cursor.execute("""CREATE TABLE made
                  (id INTEGER, zakaz INTEGER, summ TEXT, result TEXT, comment TEXT, truth BOOLEAN, agree BOOLEAN)
               """)
except:
    exc = True

conn.commit()
conn.close()

