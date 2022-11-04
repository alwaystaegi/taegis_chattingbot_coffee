from flask import Flask, render_template, request
from bs4 import BeautifulSoup as bs
from collections import Counter
from konlpy.tag import Okt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re as r
import time
import random




options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome (service=Service(ChromeDriverManager().install()),options=options)

driver.implicitly_wait(0.5)
okt=Okt()


tags={}
beverage={}
list_url="https://www.starbucks.co.kr/menu/drink_list.do"#스타벅스 음료목록페이지
item_url="https://www.starbucks.co.kr/menu/drink_view.do?product_cd="#음료 상세페이지
nonword=['Josa','Punctuation','Foreign']#불필요한 품사목록
stopword=['이다','있다','보다','같다','살리다','특징','로써','맛','즐기다','수','시키다','되어다']#불필요한 단어 목록... 모든걸 추가하긴 어렵고 우선 자주 보인 단어들만 넣어두었음.

driver.get(list_url)
driver.maximize_window()
source_code = driver.find_element(By.CSS_SELECTOR,'.product_list > dl')
# print(source_code.get_attribute('innerHTML'))
soup=bs(source_code.get_attribute('innerHTML'),"html.parser")
html=soup.select('dd')
for listhtml in html:
    itemlist=listhtml.select('a')
    for item in itemlist:
        
        
        driver.get(item_url+item.get('prod'))
        # driver.get(item_url+'9200000004117')  #test
        time.sleep(1)
        try:
            driver.switch_to.alert.accept()

        except:
            
            name = driver.find_element(By.CSS_SELECTOR,'.this').text
            while name== '':#셀레니움이 전체화면이 아니면 이름을 가져오지 않아 exception이 발생해 프로그램이 종료된다. 이를 방지하기 위한 while문
                name = driver.find_element(By.CSS_SELECTOR,'.this').text
            tag=['all']#tag변수에 string배열로 값을 입력받아 tags에 {tag:[...name]} 형식으로 추가 or 업데이트한다.
            #또한 태그와 일치하는것을 찾지 못했을때를 대비해 모든 음료를 all태그에 넣어두었다 
            tag=tag+okt.pos(driver.find_element(By.CSS_SELECTOR,'.cate').text)# css(.cate)에 음료의 종류가 있다.(ex.콜드 브루,에스프레소)

            infotext=driver.find_element(By.CSS_SELECTOR,'.myAssignZone > .t1').text#myAssignZone>.t1에 음료의 설명이 있다.
            
            beverage.setdefault(name,infotext)

            infotextpos=okt.pos(infotext,norm=True,stem=True)

            for word in infotextpos:
                if word[1] not in nonword and word[0] not in stopword and word[0].isalpha():  
                    tag.append(word[0])
            for val in tag:
                if val not in tags.keys():
                    tags.setdefault(val,[name])  
                else :tags[val].append(name)







#유저가 입력한 단어를 분리해서 태그와 일치하는 음료를 pick변수에 넣어 변수에 가장 많이 있는 음료 5가지를 반환한다.
def findbeverage(user_msg):
    msg=okt.pos(user_msg,norm=True,stem=True)
    print(msg)
    pick=[]
    for word in msg:
        if word[0] in tags:
            pick+=tags[word[0]]
    counter=Counter(pick)
    return counter.most_common(5)



# ------------------------------------Flask App -------------------------------------
app = Flask(__name__)
@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/get')
def Chatbot():

    user_msg = request.args.get('msg')

    picks=findbeverage(user_msg)
    req={}
    
    #음료 목록을 가져왔을 때 이 목록을 보내준다.
    if picks!=[]:
        req.setdefault('check',1)
        for pick in picks:
            req.setdefault(pick[0],beverage[pick[0]])
        return req
    #만약 음료 목록이 없다면 랜덤한 다섯개음료를 보내준다.    
    else: 
        picks=random.sample(tags['all'],5)
        req.setdefault('check',0)
        for pick in picks:
            req.setdefault(pick,beverage[pick])
        return req   


if __name__=="__main__":
    app.run()
