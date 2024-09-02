import requests
import tkinter as tk
#from selenium import webdriver
#from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re, json
import threading
import time, os

import openpyxl
from openpyxl.styles import Font
 
#time: 2hr, 30min

#url = "https://www.ted.com/talks/jessica_apotheker_what_will_happen_to_marketing_in_the_age_of_ai"


def write_excel(ctn, title,  out_dir):
    s_ep = f"{title}" # title

    wb = openpyxl.Workbook()
    sheet = wb.worksheets[0]

    sheet.oddHeader.center.text  = s_ep
    sheet.evenHeader.center.text = s_ep
    sheet.oddHeader.center.font  = "Arial Black"
    sheet.evenHeader.center.font = "Arial Black"

    sheet.oddHeader.center.size  = 20
    sheet.evenHeader.center.size = 20

    # ==== right page
    sheet.oddHeader.right.text  = "&P / &N"
    sheet.evenHeader.right.text = "&P / &N"
    sheet.oddHeader.right.font  = "Arial,Bold"
    sheet.evenHeader.right.font = "Arial,Bold"

    font = Font(name="Arial", size=16)
    ctns = ctn.splitlines()
    lens = len(ctns)
    for x in range(lens):
        cellref=sheet.cell(row=x + 1, column=1)
        sheet.row_dimensions[x + 1].height = 60
        cellref.value = ctns[x]
        cellref.font = font
    
    f_name = f"{title}"
    f_name = str(f_name) + ".xlsx"
    print(f_name)
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_path = f"{out_dir}/{f_name}"
    wb.save(out_path)


class TedCrawler():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Transcript crawler")
        self.window.geometry('300x300')

        self.status = tk.StringVar()   # text variable for showing crawling status
        self.status.set('')            # initialize
        self._stop = False

        tk.Label(self.window, text="URL of TED: ").grid(row=0, column=0)
        tk.Label(self.window, text="Output file name: ").grid(row=1, column=0)
        tk.Label(self.window, textvariable=self.status).grid(row=5, column=2)

        self.url    = tk.Entry()
        self.url.grid(row=0, column= 1)

        self.f_name = tk.Entry()
        self.f_name.grid(row=1, column=1)

        #btn = tk.Button(window, text="Enter", command=lambda: run_crawl(url, f_name))
        btn = tk.Button(self.window, text="Enter", command=lambda: self.run_crawl())

        #btn = tk.Button(self.window, text="Enter", command=lambda: run_crawl(self.url.get(), self.f_name.get()))
        btn.grid(row=5, column=1)

        self.t = threading.Thread(target=self.chk_state)
        self.t.start()
        self.window.mainloop()
        self._stop = True  # control the life cycle of thread

    @classmethod
    def trans_xml(cls, ctn):
        replacements = [("&quot;", '"'), ("&amp;", "&"), ("&apos;", "'"), ("&It;", "<"), ("&gt;", ">")]
        for pat, repl in replacements:
            ctn = re.sub(pat, repl, ctn)
        return ctn

    @classmethod
    def endline(cls, text):
        replacements = [("?", '\?\n'), (".", "\.\n"), ("!", "!\n"), ('\w+"', '\w+"\n'), (")", ")\n")]
        for pat, repl in replacements:
            ctn = re.sub(pat, repl, text)
        return ctn



    def run_crawl(self):
        rsp = requests.get(self.url.get())
        soup = BeautifulSoup(rsp.text, "html.parser")
        script_tags = soup.find_all('script', type="application/ld+json")

        if (len(script_tags) == 0):
            print("Parsing error!, Check your url")
            self.window.quit()
            self.t.join()
            exit(0)

        if len(script_tags) > 1:
            tk.Label(self.window, text="Check Error!").grid(row=10, column=2)
            print("check error!")
        else:
            f_name = self.f_name.get()

            cnt = script_tags[0]
            json_cnt = json.loads(cnt.text)
            #rslt = re.split(r'\.', json_cnt["transcript"])
            tmp = json_cnt["transcript"]
            rslt = self.trans_xml(tmp)

            rslt = re.sub(r'([!?.])', r'\1\n', rslt)

            #new_words = ""
            #for line in rslt.splitlines():
            #    words = re.split(r'\s+', line)
            #    if (len(words) > 10):
            #        lines = [' '.join(words[i:i+10]) for i in range(0, len(words), 10)]
            #        temp = '\n'.join(lines)
            #        new_words += temp + '\n'
            #    else:
            #        new_words += line + '\n'

            #write_excel(new_words, f_name, "result")

            f_name = self.f_name.get() + ".txt"

            folder = os.path.dirname(f_name)
            if folder != "" and not os.path.exists(folder):
                os.makedirs(folder)
            with open(f_name, "w") as fw:
                fw.write(rslt)
            self.reset()
            #tk.Label(self.window, text="Finish!").grid(row=5, column=2)
            self.status.set("Finish!")
    
    def reset(self):
        self.url.delete(0, tk.END)
        self.f_name.delete(0, tk.END)

    def chk_state(self): # check the finish state per 1 sec => TODO. listener: listen the url, file name Entry
        while self._stop != True:
            if (self.url.get()!="" or self.f_name.get()!=""):
                self.status.set("")
            time.sleep(1)


app = TedCrawler()

#url = input("enter the url of ted: ")
#f_name = input("Enter the name of output file: ")
#run_crawl(url, f_name)