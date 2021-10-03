# -*- coding = utf-8 -*-
# @Time : 2021/8/24 17:34
# @Author : Ram
# @File : spider.py
# @Software : PyCharm

from bs4 import BeautifulSoup  # 网页解析，获取数据
import re                      # 正则表达式，进行文字匹配
import urllib.request          # 指定url，获取网页数据
import urllib.error            # urllib error
import xlwt                    # 进行excel操作
import sqlite3                 # 进行sqlite操作

# ---------全局变量---------
find_link = re.compile(r'<a href="(.*?)">')                 # 创建正则表达式对象，表示规则（字符串的模式）
find_imgsrc = re.compile(r'<img.*src="(.*?)"', re.S)      # re.S忽视换行符
find_title = re.compile(r'<span class="title">(.*)</span>') # 片名
find_rating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>') # 评分
find_judge = re.compile(r'<span>(\d*)人评价</span>')         # 评价人数
find_inq = re.compile(r'<span class="inq">(.*)</span>')     # 一句话简介
find_bd = re.compile(r'<p class="">(.*?)</p>', re.S)        # 相关内容


def main():
    baseurl = "https://movie.douban.com/top250?start="
    data_list = get_data(baseurl)
    # save_path = "豆瓣电影top250.xls"
    db_path = "movie.db"
    # save_data(data_list, save_path)
    save_dava_2db(data_list, db_path)


# 爬取网页
def get_data(baseurl):
    data_list = []
    for i in range(0, 10): # 左闭右开
        url = baseurl + str(i * 25)
        html = askURL(url)

        # 逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_= "item"): # 查找符合要求的字符串，并存到列表中
            data = []                                     # 保存一部电影的所有信息
            item = str(item)                              # 转成字符串

            link = re.findall(find_link, item)[0]
            data.append(link)

            imgsrc = re.findall(find_imgsrc, item)[0]
            data.append(imgsrc)

            title = re.findall(find_title, item)
            if len(title) == 2:                           # 有一个中文名，后面紧跟一个外文名
                ctitle = title[0]
                data.append(ctitle)
                title[1] = title[1].replace("/", "")        # 将其中的/替换掉
                title[1] = title[1].replace("\xa0", "")     # 将其中的\xa0替换掉
                data.append(title[1])
            else:                                         # 只有一个中文名
                data.append(title[0])
                data.append(" ")                          # 后面保存数据时，外文名可能为空，但必须存在


            rating = re.findall(find_rating, item)[0]
            data.append(rating)

            judge = re.findall(find_judge, item)[0]
            data.append(judge)

            inq = re.findall(find_inq, item)
            if len(inq) != 0:
                data.append(inq[0])
            else:
                data.append(" ")

            bd = re.findall(find_bd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', " ", bd)     # 去掉<br/>
            bd = bd.replace("\xa0", "")
            data.append(bd.strip())                       # 去掉空格

            data_list.append(data)                        # 把处理好的一部电影放data_list中
    print(data_list)
    return data_list

# 得到指定url的网页内容
def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 = Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }
    req = urllib.request.Request(url, headers = head)
    html = ""
    try:
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8')

    except urllib.error.URLError as e:
        if hasattr(e, "code"): # 判断对象是否包含对应的属性
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    return html


# 保存数据到excel表中
def save_data(data_list, save_path):
    print("saving...")
    wb = xlwt.Workbook(encoding = "utf-8", style_compression = 0)
    ws = wb.add_sheet('豆瓣电影top250', cell_overwrite_ok = True)

    col = ("电影详情链接", "图片链接", "中文名", "外文名", "评分", "评价人数", "概况", "相关信息")
    for i in range(0, 8):
        ws.write(0, i, col[i])
    for i in range(0, 250):
        data = data_list[i]
        for j in range(0, 8):
            ws.write(i + 1, j, data[j])

    wb.save(save_path)


# 保存数据到sqlite中
def save_dava_2db(data_list, db_path):
    init_db(db_path)
    conn = sqlite3.connect(db_path) # 查询数据
    cursor = conn.cursor()
    for data in data_list:
        for j in range(len(data)):
            if j == 4 or j == 5:
                continue
            data[j] = '"' + data[j] + '"'
        sql = '''
            insert into movie250(info_link, pic_url, c_title, o_title, score, rated, intro, info)
            values(%s)'''%",".join(data)

        cursor.execute(sql)
        conn.commit()
        # print(sql)
    cursor.close()
    conn.close()




# 初始化sqlite数据表
def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql = '''
        create table movie250
            (id integer primary key autoincrement,
            info_link text,
            pic_url text,
            c_title varchar,
            o_title varchar,
            score numeric,
            rated numeric,
            intro text,
            info text);
    '''
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()