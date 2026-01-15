import telebot
import random
import json
import os

BOT_TOKEN = "8549639912:AAGqomQqnsKkuIGnxPTxvdn4OCumrUwHDFc"
ADMIN_ID = 728406891

bot = telebot.TeleBot(BOT_TOKEN)
DB = "keys.json"

def load():
    try:
        if os.path.exists(DB):
            with open(DB) as f:
                return json.load(f)
    except:
        pass
    return {"keys":{}}

def save(d):
    with open(DB,"w") as f:
        json.dump(d,f)

def genkey():
    c="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return f"{''.join(random.choices(c,k=4))}-{''.join(random.choices(c,k=4))}-{''.join(random.choices(c,k=4))}"

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m,"🚀 *Nexora Key Bot*\n\n/getkey - Get key\n/status - Check status\n\nAdmin: /admin",parse_mode="Markdown")

@bot.message_handler(commands=['getkey'])
def getkey(m):
    db=load()
    uid=m.from_user.id
    for k,v in db["keys"].items():
        if v.get("uid")==uid:
            bot.reply_to(m,f"⚠️ You have key!\n\n🔑 `{k}`",parse_mode="Markdown")
            return
    key=genkey()
    db["keys"][key]={"uid":uid,"device":None,"active":True}
    save(db)
    bot.reply_to(m,f"✅ *Key Generated!*\n\n🔑 `{key}`\n\nUse in Nexora App",parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def status(m):
    db=load()
    uid=m.from_user.id
    for k,v in db["keys"].items():
        if v.get("uid")==uid:
            s="✅ Active" if v.get("active") else "❌ Banned"
            d="📱 Linked" if v.get("device") else "⏳ Not linked"
            bot.reply_to(m,f"🔑 `{k}`\n{s}\n{d}",parse_mode="Markdown")
            return
    bot.reply_to(m,"❌ No key! Use /getkey")

@bot.message_handler(commands=['admin'])
def admin(m):
    if m.from_user.id!=ADMIN_ID:
        return
    bot.reply_to(m,"👑 *Admin*\n\n/stats\n/allkeys\n/genkey\n/ban KEY\n/unban KEY\n/reset KEY\n/del KEY",parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats(m):
    if m.from_user.id!=ADMIN_ID:
        return
    db=load()
    t=len(db["keys"])
    a=sum(1 for v in db["keys"].values() if v.get("active"))
    l=sum(1 for v in db["keys"].values() if v.get("device"))
    bot.reply_to(m,f"📊 *Stats*\n\n🔑 Total: {t}\n✅ Active: {a}\n📱 Linked: {l}",parse_mode="Markdown")

@bot.message_handler(commands=['allkeys'])
def allkeys(m):
    if m.from_user.id!=ADMIN_ID:
        return
    db=load()
    if not db["keys"]:
        bot.reply_to(m,"📭 No keys")
        return
    txt="🔑 *Keys:*\n\n"
    for k,v in db["keys"].items():
        s="✅" if v.get("active") else "❌"
        d="📱" if v.get("device") else "⏳"
        txt+=f"{s} `{k}` {d}\n"
    bot.reply_to(m,txt,parse_mode="Markdown")

@bot.message_handler(commands=['genkey'])
def adminkey(m):
    if m.from_user.id!=ADMIN_ID:
        return
    db=load()
    key=genkey()
    db["keys"][key]={"uid":ADMIN_ID,"device":None,"active":True}
    save(db)
    bot.reply_to(m,f"✅ Key: `{key}`",parse_mode="Markdown")

@bot.message_handler(commands=['ban'])
def ban(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        key=m.text.split()[1].upper()
        db=load()
        if key in db["keys"]:
            db["keys"][key]["active"]=False
            save(db)
            bot.reply_to(m,f"✅ Banned: `{key}`",parse_mode="Markdown")
        else:
            bot.reply_to(m,"❌ Not found")
    except:
        bot.reply_to(m,"Usage: /ban KEY")

@bot.message_handler(commands=['unban'])
def unban(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        key=m.text.split()[1].upper()
        db=load()
        if key in db["keys"]:
            db["keys"][key]["active"]=True
            save(db)
            bot.reply_to(m,f"✅ Unbanned: `{key}`",parse_mode="Markdown")
        else:
            bot.reply_to(m,"❌ Not found")
    except:
        bot.reply_to(m,"Usage: /unban KEY")

@bot.message_handler(commands=['reset'])
def reset(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        key=m.text.split()[1].upper()
        db=load()
        if key in db["keys"]:
            db["keys"][key]["device"]=None
            save(db)
            bot.reply_to(m,f"✅ Reset: `{key}`",parse_mode="Markdown")
        else:
            bot.reply_to(m,"❌ Not found")
    except:
        bot.reply_to(m,"Usage: /reset KEY")

@bot.message_handler(commands=['del'])
def delete(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        key=m.text.split()[1].upper()
        db=load()
        if key in db["keys"]:
            del db["keys"][key]
            save(db)
            bot.reply_to(m,f"✅ Deleted: `{key}`",parse_mode="Markdown")
        else:
            bot.reply_to(m,"❌ Not found")
    except:
        bot.reply_to(m,"Usage: /del KEY")

@bot.message_handler(commands=['verify'])
def verify(m):
    try:
        p=m.text.split()
        key=p[1].upper()
        dev=p[2] if len(p)>2 else "unknown"
        db=load()
        if key not in db["keys"]:
            bot.reply_to(m,"INVALID")
            return
        kd=db["keys"][key]
        if not kd.get("active"):
            bot.reply_to(m,"BANNED")
            return
        if kd.get("device") is None:
            db["keys"][key]["device"]=dev
            save(db)
            bot.reply_to(m,"ACTIVATED")
            return
        if kd.get("device")==dev:
            bot.reply_to(m,"VALID")
            return
        bot.reply_to(m,"DEVICE_MISMATCH")
    except:
        bot.reply_to(m,"ERROR")

print("✅ Bot Started!")
bot.infinity_polling()
