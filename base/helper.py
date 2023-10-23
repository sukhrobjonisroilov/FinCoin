#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
import datetime

from django.conf import settings
from random import randint


def unique_card():
    number = "8800 " + " ".join([str(randint(1000, 9999)) for x in range(3)])
    with open("base/numbers.txt", "r") as file:
        if number not in file.read().replace('\n', '').split(","):
            file = open("base/numbers.txt", "a")
            file.write(number + ",\n")
            return number
        else:
            return unique_card()


def lang_helper(request):
    if not request.user.is_anonymous:
        return request.user.lang
    return settings.DEFAULT_LANG


def card_mask(number):
    return number[0:4] + ' **** ****' + number[14:]


def generate_number():
    return unique_card()


def cusmot_dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = []
    for i in cursor.description:
        columns.append(i[0])
    a = cursor.fetchall()
    img = None
    if "img" in columns:
        img = columns.index("img")
    natija = []
    for i in a:
        i = list(i)
        if img:
            i[img] = f"{settings.HOST_URL}/media/" + i[img]
        b = dict(zip(columns, i))
        natija.append(b)
    return natija


def custom_dictfetchone(cursor):
    columns = [i[0] for i in cursor.description]
    row = cursor.fetchone()
    if row is not None:
        img = None
        if "img" in columns:
            img = columns.index("img")
        row = list(row)
        if img is not None:
            row[img] = f"{settings.HOST_URL}/media/" + row[img]
        return dict(zip(columns, row))
    else:
        return None


def look_at_params(params: dict, requires: list):
    return set(requires) - set(params.keys())


def make_transfer(sender, receiver, amount: int):
    try:
        sender.balance = sender.balance - amount
        receiver.balance = receiver.balance + amount
    except:
        return False
    sender.save(), receiver.save()
    return True

