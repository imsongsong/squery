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
    codeList = []
    with open("setting.txt", "r") as f:
        hkStockList = f.readline().split(":")[1].replace('\n', '').split(";")
        chStockList = f.readline().split(":")[1].split(";")
        for cnStock in chStockList:
            if cnStock[0] == "3" or cnStock[0] == "0":
                codeList.append('s_sz' + cnStock)
            else:
                codeList.append('s_sh' + cnStock)

        for hkStock in hkStockList:
            codeList.append('hk' + hkStock)

    tmpResult = requests.get(
        'https://hq.sinajs.cn/list=' + ','.join(codeList)).text

    for idx, tmp in enumerate(tmpResult.split('\n')):
        if '""' in tmp or "FAILED" in tmp or "" == tmp:
            continue
        print(tmp)
        if idx < len(chStockList):
            tmp = tmp.split('"')[1].split(',')
            result.append(lineFormat.format(
                tmp[0]+codeList[idx], tmp[1][0:-1], tmp[3]))
        else:
            tmp = tmp.split('"')[1].split(',')
            result.append(lineFormat.format(
                tmp[1]+codeList[idx], tmp[6][0:-1], str(round(float(tmp[7]) * 100 / float(tmp[3]), 2))))

    return "".join(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
