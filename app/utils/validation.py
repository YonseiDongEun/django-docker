import re
from datetime import date
from app.utils import dbinterface

def user_id(uid):
    if not(2<=len(uid)<=15):
        return "ID should be between 2 and 15 characters long"
    if re.match("^[a-zA-Z_][0-9a-zA-Z_]{0,14}$",uid) is None:
        return "ID should start with alphabet or underscore, and consist of alphanumeric or underscore."
    return None

def birth(brt):
    tdy = date.today()
    if(brt is None):
        return None
    if(tdy<brt):
        return "Birthday should be earlier than today."
    return None

def password(pw):
    if(len(pw)==0):
        return None
    return password_init(pw)

def password_init(pw):
    if not(2<=len(pw)<=20):
        return "Password should be between 2 and 20 characters long."
    return None

def phone(ph):
    if not(len(ph)<=11):
        return "Phone number is at most 11 characters long."
    return None

def address(addr):
    if not(len(addr)<=64):
        return "Address is at most 64 characters long."
    return None

def name(nm):
    if not(len(nm)<=15):
        return "Name is at most 15 characters long."
    return None

def validate(func,val,lst):
    result = func(val)
    if(result is not None):
        lst.append(result)
    return

def display_name(dn):
    if not(2<=len(dn)<=15):
        return "Display Name should be between 2 and 15 characters long."
    return None

def description(dsc):
    if not(len(dsc)<=100):
        return "Description is at most 100 characters long."
    return None
