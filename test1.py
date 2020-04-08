from tkinter import *
import shelve

root = Tk()
root.geometry("300x300")

#
frame1 = Frame(root)
frame1.pack(side=TOP)

frame2 = Frame(root)
frame2.pack(side=TOP)
#
#
label_login = Label(frame1, text="Login")
label_login.pack(side=LEFT)

label_password = Label(frame2, text="password")
label_password.pack(side=LEFT)
#
#
entry_login = Entry(frame1)
entry_login.pack(side=LEFT)

entry_password = Entry(frame2)
entry_password.pack(side=LEFT)
#
#

def save_data():
    global entry_login
    global entry_password
    with shelve.open("data") as data:
        data['login'] = entry_login.get()
        data['password'] = entry_password.get()


def log_in():
    save_data()
    with shelve.open("data") as data:
        print(data["login"], data["password"])
    # client.login()
    # save_data


def insert_data():
    with shelve.open("data") as data:
        entry_login.delete(0, END)
        entry_password.delete(0, END)
        entry_login.insert(0, data["login"])
        entry_password.insert(0, data["password"])


btn1 = Button(root, text="log in", command=log_in)
btn1.pack(side=BOTTOM)

btn2 = Button(root, text="insert_data", command=insert_data)
btn2.pack(side=BOTTOM)


root.mainloop()