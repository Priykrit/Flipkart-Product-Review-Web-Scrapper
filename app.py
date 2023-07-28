from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import csv

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            w = csv.writer(fw)
            headers = ["Search", "Product", "Customer Name", "Rating", "Heading", "Comment"]
            w.writerow(headers)
            reviews = []
            try:
                    product_name = prod_html.find_all("span",{"class":"B_NuCI"})[0].text
            except:
                product_name="No name"
                logging.info("Product_name")
            
            for commentbox in commentboxes:

                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Search":searchString,"Product": product_name, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            
            client = pymongo.MongoClient("mongodb+srv://priykritv:priykrit@cluster0.gp1bff2.mongodb.net/?retryWrites=true&w=majority")
            db =client['Web_scrapper_project']
            coll_eng = db['web_scrapper']
            coll_eng.insert_many(reviews)
            for i in reviews:
                w.writerow([i['Search'],i['Product'],i['Name'],i['Rating'],i['CommentHead'],i['Comment']])
            return render_template('result.html', reviews=reviews[0:(len(reviews))])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
        finally:
            fw.close()
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
