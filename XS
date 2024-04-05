from colorama import init, Fore, Back, Style
from bs4 import BeautifulSoup as bs
import requests

from urllib.parse import urljoin
from pprint import pprint
import time


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
}

init(autoreset=True)


def stop(stop_time):
    now_time = time.time()
    if stop_time - now_time <= 0:
        return True

def save(url):
    file = open("goods.txt", "a")
    file.write(f"{url}\n")
    file.close()

def scan_xss(url, stop_time, timeout):
    stop_time = time.time() + stop_time

    html = requests.get(url, headers=headers, timeout=timeout)
    soup = bs(html.content, "html.parser")
    forms = soup.find_all("form")
    js_script = "<Script>alert('XSS')</scripT>"
    is_vulnerable = False
 
    for form in forms:
        if stop(stop_time):
            break
        details = {}

        action = form.attrs.get("action")
        method = form.attrs.get("method", "get")
 
        if action != None and not(action.startswith("javascript")):
            action = action.lower()
            method = method.lower()
        else:
            break

        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            inputs.append({"type": input_type, "name": input_name})
        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs
        form_details =  details
        target_url = urljoin(url, form_details["action"])
        inputs = form_details["inputs"]
        data = {}

        for input in inputs:
            if input["type"] == "text" or input["type"] == "search":
                input["value"] = js_script
            input_name = input.get("name")
            input_value = input.get("value")
            if input_name and input_value:
                data[input_name] = input_value

        if form_details["method"] == "post":
            content = requests.post(target_url, data=data, headers=headers, timeout=timeout).content.decode('latin-1')
        else:
            content = requests.get(target_url, params=data, headers=headers, timeout=timeout).content.decode('latin-1')

        if js_script in content:
            save(url)
            print(f"{Fore.RED}[+] XSS Detected on {url}{Style.RESET_ALL}\n[*] Form details:")
            pprint(form_details)


if __name__ == "__main__":
    urls = open('site.txt', 'r', encoding="UTF-8")
    for element in urls:
        url = element.replace("\n", "")
        print(f"\033[37m{url}")
        # Максимальное время проверки одного сайта в секундах (не менее 180)
        stop_time = 180
        # Максимальное время ожидания ответа от сайта в секундах (не менее 15)
        timeout = 20
        try:
            scan_xss(url, 180, 20)
        except:
            pass # ваще похуй

    urls.close()
