
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import joblib

app = Flask(__name__)

def scrape_reviews(url):
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'}

    def getdata(url):
        try:
            r = requests.get(url, headers=HEADERS, verify=False)
            r.raise_for_status()  # Raise an exception if the response status is not successful
            return r.text
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            print(f"Error occurred during request: {e}")
            return None

    def html_code(url):
        htmldata = getdata(url)
        if htmldata:
            soup = BeautifulSoup(htmldata, 'html.parser')
            return soup
        else:
            return None

    soup = html_code(url)

    def cus_rev(soup):
        if soup is None:
            return []

        data_str = ""

        for item in soup.find_all("a", class_= "a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"):
            data_str = data_str + item.get_text()

        result = data_str.split("\n")
        return result

    rev_data = cus_rev(soup)
    rev_result = []
    for i in rev_data:
        if i != "":
            rev_result.append(i)
    return rev_result


def classify_reviews(reviews):
    model = joblib.load('ranfor.pkl')
    predictions = []
    good_count = 0  # Counter for good reviews
    bad_count = 0   # Counter for bad reviews
    
    for review in reviews:
        prediction = model.predict([review])
        predictions.append(prediction[0])

        if prediction[0] == 'pos':
            good_count += 1
        else:
            bad_count += 1

    return predictions, good_count, bad_count


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/classify', methods=['POST'])
def classify():
    url = request.form['url']
    reviews = scrape_reviews(url)
    predictions, good_count, bad_count = classify_reviews(reviews)

    return render_template('index.html', reviews=reviews, predictions=predictions, good_count=good_count, bad_count=bad_count)



if __name__ == '__main__':
    app.run(debug=True)
