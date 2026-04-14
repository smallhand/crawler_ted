import requests
import tkinter as tk
import re 
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        rsp = requests.get(self.url.get(), headers=headers)
        match = re.search(r'pm(\d+)-im(\d+)', rsp.text)
        if not match:
            tk.Label(self.window, text="Check Error!").grid(row=10, column=2)
            print("❌ can't find projectMasterId 或 introMasterId")
            return None
        
        pm_id = match.group(1)
        im_id = match.group(2)

        vtt_url = f"https://hls.ted.com/project_masters/{pm_id}/subtitles/en/full.vtt?intro_master_id={im_id}"
        vtt_response = requests.get(vtt_url, headers=headers)
        vtt_response.raise_for_status()
        vtt_text = vtt_response.text

        clean_text = self.clean_vtt_content(vtt_text)

        f_name = self.f_name.get() + ".txt"
        folder = os.path.dirname(f_name)

        if folder != "" and not os.path.exists(folder):
            os.makedirs(folder)
        with open(f_name, "w") as fw:
            fw.write(clean_text)
        self.reset()
        self.status.set("Finish!")
    
    def clean_vtt_content(self, vtt_text):
        lines = vtt_text.splitlines()
        final_lines = []
        
        for line in lines:
            # remove WEBVTT header, timestamp (contains -->), and blank line
            if line.strip() == "WEBVTT" or "-->" in line or not line.strip():
                continue
            
            # remove HTML tag (eg. <c.color...>)
            clean_line = re.sub(r'<[^>]+>', '', line)
            final_lines.append(clean_line)
        
        return " ".join(final_lines)

    
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