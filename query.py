from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    html_doc = requests.get(
        'https://hq.sinajs.cn/list=hk00700').text
    return '<div>设置</div>'+html_doc


@app.route("/setting", methods=['GET', 'POST'])
def get_setting():
    if request.method == 'GET':
        return render_template('setting.html')
    else:
        with open("setting.txt", "w") as f:
            f.write("Woops! I have deleted the content!")
        return jsonify(isError=False,
                       message="Success",
                       statusCode=200,
                       data=request.form)


if __name__ == "__main__":
    app.run()
