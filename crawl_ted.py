import requests
import tkinter as tk
#from selenium import webdriver
#from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re, json
import threading
import time
 
#time: 2hr, 30min


#url = "https://www.ted.com/talks/jessica_apotheker_what_will_happen_to_marketing_in_the_age_of_ai"
#url = input("Enter the url of TED: ")
#f_name = input("Enter the name of output file: ")
#driver = webdriver.Chrome()
#driver.get(url)
# btn = driver.find_element(By.XPATH, '//button[text()="Read transcript"]')
# btn.click()
#driver.quit()

def trans_xml(ctn):
    replacements = [("&quot;", '"'), ("&amp;", "&"), ("&apos;", "'"), ("&It;", "<"), ("&gt;", ">")]
    for pat, repl in replacements:
        ctn = re.sub(pat, repl, ctn)
    return ctn

class gui():
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
        btn.grid(row=5, column=1)

        t = threading.Thread(target=self.chk_state)
        t.start()
        self.window.mainloop()
        self._stop = True  # control the life cycle of thread

    def run_crawl(self):
        rsp = requests.get(self.url.get())
        soup = BeautifulSoup(rsp.text, "html.parser")
        script_tags = soup.find_all('script', type="application/ld+json")

        if len(script_tags) > 1:
            tk.Label(self.window, text="Check Error!").grid(row=10, column=2)
            print("check error!")
        else:
            cnt = script_tags[0]
            json_cnt = json.loads(cnt.text)
            #rslt = re.split(r'\.', json_cnt["transcript"])
            tmp = json_cnt["transcript"]
            rslt = trans_xml(tmp)

            #f_name = "transcript.txt"
            f_name = self.f_name.get() + ".txt"
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

app = gui()