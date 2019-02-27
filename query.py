# from bs4 import BeautifulSoup
import requests
import threading
from flask import Flask, render_template, request, jsonify
from multiprocessing.pool import ThreadPool


app = Flask(__name__)
lineFormat = '<div class="line"><span class="stock">{}</span><span class="price">{}</span><span class="diff">{}%</span></div>'


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
    result = []
    threads = []
    with open("setting.txt", "r") as f:
        hkStockList = f.readline().split(":")[1].replace('\n', '').split(";")
        for hkStock in hkStockList:
            t = threading.Thread(target=queryHK, args=(hkStock, result))
            threads.append(t)
            t.start()

        chStockList = f.readline().split(":")[1].split(";")
        for cnStock in chStockList:
            t = threading.Thread(target=queryCN, args=(cnStock, result))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

    result.sort()
    return "".join(result)


def queryHK(code, result):
    tmp = requests.get('https://hq.sinajs.cn/list=hk' + code).text
    if '""' in tmp or "FAILED" in tmp:
        return
    tmp = tmp.split('"')[1].split(',')
    result.append(lineFormat.format(
        tmp[1], tmp[6][0:-1], str(round(float(tmp[7]) * 100 / float(tmp[3]), 2))))


def queryCN(code, result):
    if code[0] == "3":
        tmp = requests.get('https://hq.sinajs.cn/list=s_sz' + code).text
    else:
        tmp = requests.get('https://hq.sinajs.cn/list=s_sh' + code).text

    if '""' in tmp or "FAILED" in tmp:
        return
    tmp = tmp.split('"')[1].split(',')
    result.append(lineFormat.format(tmp[0], tmp[1][0:-1], tmp[3]))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
