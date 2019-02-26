# from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, jsonify
from multiprocessing.pool import ThreadPool


app = Flask(__name__)


@app.route("/setting", methods=['GET', 'POST'])
def setting():
    if request.method == 'GET':
        with open("setting.txt", "r") as f:
            hkStockList = "\n".join(f.readline().split(":")[1].split(";"))
            chStockList = "\n".join(f.readline().split(":")[1].split(";"))
        return render_template('setting.html', hkStockList=hkStockList, chStockList=chStockList)
    else:
        with open("setting.txt", "w") as f:
            hkStockList = request.form['hkStockList'].split("\n")
            f.write("hkStockList:"+";".join(hkStockList) + "\n")
            chStockList = request.form['chStockList'].split("\n")
            f.write("chStockList:"+";".join(chStockList))
        return jsonify(isError=False,
                       message="Success",
                       statusCode=200)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/query")
def query():
    result = ""
    with open("setting.txt", "r") as f:
        hkStockList = f.readline().split(":")[1].replace('\n', '').split(";")
        for hkStock in hkStockList:
            tmp = requests.get('https://hq.sinajs.cn/list=hk' + hkStock).text
            if '""' in tmp or "FAILED" in tmp:
                continue
            tmp = tmp.split('"')[1].split(',')
            result += '<div class="line"><span class="stock">' + \
                tmp[1] + '</span><span class="price">' + \
                tmp[6][0:-1] + '</span><span class="diff">' + \
                str(round(float(tmp[7]) * 100 /
                          float(tmp[3]), 2)) + '%</span></div>'

        chStockList = f.readline().split(":")[1].split(";")
        for hkStock in chStockList:
            tmp = requests.get('https://hq.sinajs.cn/list=s_sh' + hkStock).text
            if '""' in tmp or "FAILED" in tmp:
                tmp = requests.get(
                    'https://hq.sinajs.cn/list=s_sz' + hkStock).text
                if '""' in tmp or "FAILED" in tmp:
                    continue
            tmp = tmp.split('"')[1].split(',')
            result += '<div class="line"><span class="stock">' + \
                tmp[0] + '</span><span class="price">' + \
                tmp[1][0:-1] + '</span><span class="diff">' + \
                tmp[3] + '%</span></div>'

    return result


def queryHK(code):
    tmp = requests.get('https://hq.sinajs.cn/list=hk' + code).text
    if '""' in tmp or "FAILED" in tmp:
        return
    tmp = tmp.split('"')[1].split(',')
    return '<div class="line"><span class="stock">' + \
        tmp[1] + '</span><span class="price">' + \
        tmp[6][0:-1] + '</span><span class="diff">' + \
        str(round(float(tmp[7]) * 100 /
                  float(tmp[3]), 2)) + '%</span></div>'


if __name__ == "__main__":
    app.run()
