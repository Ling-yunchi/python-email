import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk

from src.mailutil import MailUtil, get_pop_host, get_smtp_host

success_bg_color = "#02B875"
warnings_bg_color = "#F0AD4E"
info_bg_color = "#17A2B8"


class App:
    now_frame: None | tk.Frame = None
    login = False
    mail_util: None | MailUtil = None

    def __init__(self, root):
        # set title
        root.title('Email Client')

        # center the window
        width = 600
        height = 400
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        # root.resizable(False, False)

        # create a left bar
        left_bar = ttk.Frame(root, width=200, height=400, bootstyle='success', padding=10)
        left_bar.pack(side=tk.LEFT, fill=tk.Y)

        label = ttk.Label(left_bar, text='163 Mail Client', font=('Arial', 15), background=success_bg_color,
                          foreground='white')
        label.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.login_button = ttk.Button(left_bar, text='Login', command=self.show_login_frame)
        self.login_button.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.get_email_button = ttk.Button(left_bar, text='Get Email', width=10, command=self.show_get_email_frame,
                                           state=tk.DISABLED)
        self.get_email_button.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.send_email_button = ttk.Button(left_bar, text='Send Email', width=10, command=self.show_send_email_frame,
                                            state=tk.DISABLED)
        self.send_email_button.pack(side=tk.TOP, fill=tk.X, pady=10)

        # create a right main widget
        self.right_main = ttk.Frame(root, width=400, height=400, bootstyle='warning', padding=10)
        self.right_main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # create a welcome frame
        self.welcome_frame = ttk.Frame(self.right_main, width=400, height=100, bootstyle='info', padding=50)
        self.now_frame = self.welcome_frame
        self.now_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # center the label
        label = ttk.Label(self.welcome_frame, text='Welcome to 163 Mail Client', font=('Arial', 15),
                          background=info_bg_color, foreground='white')
        label.pack(side=tk.TOP, fill=tk.X, pady=10)

        # create a login frame
        self.login_frame = ttk.Frame(self.right_main, width=400, height=100, bootstyle='info', padding=10)

        login_label = ttk.Label(self.login_frame, text='Login', font=('Arial', 15))
        login_label.pack(fill=tk.BOTH)

        # create a login form
        login_form = ttk.Frame(self.login_frame, width=400, height=100, bootstyle='info', padding=10)
        login_form.pack(fill=tk.BOTH, expand=True)

        email_label = ttk.Label(login_form, text='Email:')
        email_label.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.email_entry = ttk.Entry(login_form, width=30)
        self.email_entry.pack(side=tk.TOP, fill=tk.X, pady=10)
        password_label = ttk.Label(login_form, text='Password:')
        password_label.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.password_entry = ttk.Entry(login_form, width=30, show='*')
        self.password_entry.pack(side=tk.TOP, fill=tk.X, pady=10)

        # set debug value
        self.email_entry.insert(0, '18873564337@163.com')
        self.password_entry.insert(0, 'BJJTOUKRFYPZRYIS')

        self.login_button = ttk.Button(login_form, text='Login', command=self.login)
        self.login_button.pack(side=tk.TOP, fill=tk.X, pady=10)

        # create a get email frame
        self.get_email_frame = ttk.Frame(self.right_main, width=400, height=100, bootstyle='info')

        label = ttk.Label(self.get_email_frame, text='Get Email', font=('Arial', 15))
        label.pack(fill=tk.BOTH)

        # mail list
        self.mail_list = tk.Listbox(self.get_email_frame, width=30, height=10)
        self.mail_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # create a scrollbar
        self.scrollbar = ttk.Scrollbar(self.mail_list)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mail_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.mail_list.yview)

        # create a send email frame
        self.send_email_frame = ttk.Frame(self.right_main, width=400, height=100, bootstyle='info')
        label = ttk.Label(self.send_email_frame, text='Send Email', font=('Arial', 15))
        label.pack(fill=tk.BOTH)

    def show_login_frame(self):
        self.now_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        self.now_frame = self.login_frame

    def show_get_email_frame(self):
        if self.mail_util is None:
            messagebox.showinfo('Error', 'Please login first')
            return

        self.now_frame.pack_forget()
        self.get_email_frame.pack(fill=tk.BOTH, expand=True)
        self.now_frame = self.get_email_frame

        self.mail_list.delete(0, tk.END)
        for mail in self.mail_util.get_mails():
            mail_text = ttk.Text(self.mail_list, width=40, height=10, font=('Arial', 10), wrap=tk.WORD, )
            mail_text.insert(tk.END, mail.__str__())
            mail_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            self.mail_list.insert(tk.END, mail_text)

    def show_send_email_frame(self):
        self.now_frame.pack_forget()
        self.send_email_frame.pack(fill=tk.BOTH, expand=True)
        self.now_frame = self.send_email_frame

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if email == '' or password == '':
            messagebox.showinfo('Error', 'Email or password can not be empty')
            return
        pop_host = get_pop_host(email)
        smtp_host = get_smtp_host(email)
        if pop_host == '' or smtp_host == '':
            messagebox.showinfo('Error', "Can't find the email's host")
            return
        try:
            self.mail_util = MailUtil(pop_host, smtp_host, email, password)
        except Exception as e:
            messagebox.showinfo('Error', str(e))
            return
        messagebox.showinfo('Success', 'Login Success')
        self.get_email_button.config(state=tk.NORMAL)
        self.send_email_button.config(state=tk.NORMAL)
        self.show_get_email_frame()


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
