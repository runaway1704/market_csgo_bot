import requests
import schedule
import time
from steampy.client import SteamClient, TradeOfferState
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import webbrowser
import socket
import shelve


def connect_to_sever():
    sock = socket.socket()
    sock.connect(('104.18.8.154', 8080))


def update_inventory():
    req = requests.get("https://market.csgo.com/api/v2/update-inventory/?key={}".format(market_api_key))
    return req


def are_credentials_filled() -> bool:
    return api_key != '' or steamguard_path != '' or username != '' or password != '' or market_api_key != ''


def turn_on_selling():  # включает продажи(подавать запрос раз на 3 минуты)
    r = requests.get(
        "https://market.csgo.com/api/v2/ping?key={}".format(market_api_key))
    return r


def trade_request_take():  # Создать запрос на передачу КУПЛЕНЫХ ПРЕДМЕТОВ
    req = requests.get(
        "https://market.csgo.com/api/v2/trade-request-take?key={}".format(market_api_key))
    try:
        req_json = req.json()  # добавил это, надеюсь сработает
    except:
        return
    success = req_json.get("success", "")
    if success:  # проверка на создание трейда, а ниже,  собственно, его принятие
        offers = client.get_trade_offers()['response'][
            'trade_offers_received']  # offers = client.get_trade_offers()["response"]["trade_offers_sent"]
        for offer in offers:
            if is_donation(offer):
                offer_id = offer['tradeofferid']
                num_accepted_items = len(offer['items_to_receive'])
                client.accept_trade_offer(offer_id)
                with open("log.txt", "a") as somefile:
                    somefile.write("Trade was accepted at: " + time.strftime("%d/%m/%Y, %H:%M:%S",
                                                                             time.localtime()) + " you received {} items\n".format(
                        num_accepted_items))
                update_inventory()


def trade_request_give_p2p():  # Запросить данные для передачи предмета ПОКУПАТЕЛЮ (только для CS:GO)
    response_market = requests.get(
        "https://market.csgo.com/api/v2/trade-request-give-p2p?key={}".format(market_api_key))
    try:
        response_market_json = response_market.json()  # добавил это, надеюсь сработает
    except:
        return
    success_market = response_market_json.get("success", "")
    if success_market:
        response_steam = requests.get(
            "https://api.steampowered.com/IEconService/GetTradeOffers/v1/?key={}&get_sent_offers=1&historical_only".format(
                api_key))
        offer = response_steam.json()["response"]["trade_offers_sent"][0]
        trade_offer_id = offer["tradeofferid"]  # данные стима
        try:
            client._confirm_transaction(trade_offer_id)
            len_of_confirmed_trade = len(offer["items_to_give"])
            with open("log.txt", "a") as somefile:
                somefile.write("Trade was confirmed at: " + time.strftime("%d/%m/%Y, %H:%M:%S",
                                                                          time.localtime()) + " you sold {} items\n".format(
                    len_of_confirmed_trade))
            update_inventory()
        except:
            pass


def auto_accept_donation_trade_offers():
    offers = client.get_trade_offers()['response']['trade_offers_received']
    for offer in offers:
        if is_donation(offer):
            offer_id = offer['tradeofferid']
            client.accept_trade_offer(offer_id)


def is_donation(offer: dict) -> bool:
    return offer.get('items_to_receive') \
           and not offer.get('items_to_give') \
           and offer['trade_offer_state'] == TradeOfferState.Active \
           and not offer['is_our_offer']


def market_scheduler():
    connect_to_sever()
    turn_on_selling()
    trade_request_take()
    trade_request_give_p2p()
    auto_accept_donation_trade_offers()
    schedule.every(3.1).minutes.do(connect_to_sever)
    schedule.every(3.1).minutes.do(turn_on_selling)
    schedule.every(1.5).minutes.do(trade_request_take)
    schedule.every(1.5).minutes.do(trade_request_give_p2p)
    schedule.every(1.1).minutes.do(auto_accept_donation_trade_offers)
    while True:
        try:
            schedule.run_pending()  # здесь JSONDecoder error выдаёт, попробовал так сделать, хз вообще что с ним делать
        except:
            return
            # continue или break я не пробовал


win = Tk()
win.geometry("380x500")
win.maxsize(width=380, height=425)
win.title("Entry to bot")
win.configure(bg="pink")


def create_widgets():
    root = Tk()
    root.title("Market Bot")
    root.maxsize(width=300, height=400)  # 230
    root.geometry("300x400")

    frame = Frame(root, bg='gray', height=40)
    frame.pack(side="top", fill="x")

    label = Label(frame, text="Market Bot", font="Arial 16", padx=3, pady=10)
    label.pack()

    label1 = Label(root, text="This bot can accept all trade offers", font="Arial 14", bg="skyblue", padx=3, pady=10)
    label1.pack(side=TOP)

    frame1 = Frame(root)
    frame1.pack(side=BOTTOM)

    sib = Label(root,
                text="If you get a jsonDecoder error, don’t be afraid, just\n restart the bot and try not to enter sleep mode\n on your PC, this error means that the connection\n to the server is lost.",
                font="Arial 10")
    sib.pack(side="top", fill=BOTH)

    exit_button = Button(frame1, bg='grey', text="exit", command=root.destroy, height=3, width=20)
    exit_button.pack(side=RIGHT, fill=BOTH)

    start_button = Button(frame1, bg="#007dff", text="Bot Start", command=market_scheduler, height=3, width=20)
    start_button.pack(side=LEFT, fill=BOTH)


def browse():
    path_to_steam = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=[("txt files", ".txt")])
    if path_to_steam == "":
        return
    entry_path.delete(0, END)
    entry_path.insert(0, path_to_steam)


def save_data():
    with shelve.open("data") as data:
        data["username"] = login_entry.get()
        data["password"] = password_entry.get()
        data["market_api_key"] = market_api_entry.get()
        data["api_key"] = steam_api_entry.get()
        data["steamguard_path"] = entry_path.get()


def log_in():
    global username
    global password
    global market_api_key
    global api_key
    global steamguard_path
    global client
    username = login_entry.get()
    password = password_entry.get()
    market_api_key = market_api_entry.get()
    api_key = steam_api_entry.get()
    steamguard_path = entry_path.get()
    if not are_credentials_filled():
        messagebox.showerror("Error", "You have to fill credentials")
        return
    try:
        client = SteamClient(api_key)
        client.login(username, password, steamguard_path)
        messagebox.showinfo("Success",
                            'Bot logged in successfully:' + time.strftime("%d/%m/%Y, %H:%M:%S", time.localtime()))
        save_data()
        create_widgets()
        global win
        win.destroy()
    except:
        messagebox.showerror("Error", "The account name or password that you have entered is incorrect")


def insert_data():
    with shelve.open("data") as data:
        entry_login.delete(0, END)
        entry_login.insert(0, data["username"])

        entry_password.delete(0, END)
        entry_password.insert(0, data["password"])

        entry_market_api.delete(0, END)
        entry_market_api.insert(0, data["market_api_key"])

        entry_steam_api.delete(0, END)
        entry_steam_api.insert(0, data["api_key"])

        entry_path.delete(0, END)
        entry_path.insert(0, data["steamguard_path"])


def find_market_api():
    result = webbrowser.open("https://market.csgo.com/docs-v2", new=1)
    return result


def find_steam_api():
    result = webbrowser.open("https://gamerask.ru/100/kak-poluchit-steam-web-api-key", new=1)
    return result


def find_shared_secret():
    result = webbrowser.open(
        "https://github.com/SteamTimeIdler/stidler/wiki/Getting-your-%27shared_secret%27-code-for-use-with-Auto-Restarter-on-Mobile-Authentication",
        new=1)
    return result


label = Label(win, text="Market Bot", font=("arial", 20, "bold"), bg="pink", justify=CENTER, padx=10, pady=10)
label.grid(row=0, column=0, columnspan=3, sticky="w")

label_login = Label(win, text="Login (Steam): ", bg="pink", font=("arial", 10), padx=10, pady=10)
label_login.grid(row=1, column=0, sticky="e")

login_entry = StringVar()
entry_login = Entry(win, textvariable=login_entry)
entry_login.grid(row=1, column=1)

label_password = Label(win, text="Password (Steam): ", bg="pink", font=("arial", 10), padx=10, pady=10)
label_password.grid(row=2, column=0, sticky="e")

password_entry = StringVar()
entry_password = Entry(win, textvariable=password_entry)
entry_password.grid(row=2, column=1)

label_market_api = Label(win, text="Market API: ", bg="pink", font=("arial", 10), padx=10, pady=10)
label_market_api.grid(row=3, column=0, sticky="e")

market_api_entry = StringVar()
entry_market_api = Entry(win, textvariable=market_api_entry)
entry_market_api.grid(row=3, column=1)

market_api_button = Button(win, text='?', command=find_market_api, bg="skyblue")
market_api_button.grid(row=3, column=3, columnspan=2, sticky="w")

label_steam_api = Label(win, text="Steam API: ", bg="pink", font=("arial", 10), padx=10, pady=10)
label_steam_api.grid(row=4, column=0, sticky="e")

steam_api_entry = StringVar()
entry_steam_api = Entry(win, textvariable=steam_api_entry)
entry_steam_api.grid(row=4, column=1)

steam_api_button = Button(win, text="?", command=find_steam_api, bg="skyblue")
steam_api_button.grid(row=4, column=3, columnspan=2, sticky="w")

label_steam_guard_path = Label(win, text="Steamguard file path: ", bg="pink", font=("arial", 10), padx=10, pady=10)
label_steam_guard_path.grid(row=5, column=0, sticky="e")

entry_path = Entry(win)
entry_path.grid(row=5, column=1)

entry_path_button = Button(win, text="?", command=find_shared_secret, bg="skyblue")
entry_path_button.grid(row=5, column=3, columnspan=2, sticky="w")

btn = Button(win, text="Browse", command=browse, padx=10, bg="skyblue")
btn.grid(row=5, column=2)

btn_login = Button(win, text="Log in", command=log_in, pady=5, padx=10, bg="skyblue")
btn_login.grid(row=6, column=1, sticky="w")

btn_insert_data = Button(win, text="Insert data", command=insert_data, pady=5, padx=10, bg="skyblue")
btn_insert_data.grid(row=6, column=2, sticky="w")

lbl = Label(win, text="You need to put in 'Steamguard file path' txt file in format:  ", bg="pink")
lbl.grid(row=7, column=0, columnspan=3, sticky="w")

a = """
{
    "steamid": "YOUR_STEAM_ID_64",
    "shared_secret": "YOUR_SHARED_SECRET",
    "identity_secret": "YOUR_IDENTITY_SECRET"
}
"""

lbl2 = Label(win, text=a, bg="pink")
lbl2.grid(row=8, column=0, columnspan=4, sticky="w")

win.mainloop()
