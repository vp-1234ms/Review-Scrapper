from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen 
import pymongo
###MADE BY VAIBHAV
application = Flask(__name__)
app=application

@app.route("/",methods = ['GET'])
@cross_origin()
def homepage():
    return (render_template("index.html"))

@app.route("/review" , methods = ['POST' , 'GET'])
@cross_origin()
def action_page():
    if request.method == 'POST':
        product = request.form['content1'].replace(" ","")
        flipkart_url = "https://www.flipkart.com/search?q=" 
        flipkart_url = flipkart_url + product
        urlclient=urlopen(flipkart_url)
        flipkart_page=urlclient.read()
        flipkart_html=bs(flipkart_page,"html.parser")
        bigbox=flipkart_html.find_all("div",{"class":"_1AtVbE col-12-12"})
        main_url_list=[]
        for i in bigbox:
            try:
                main_url = i.div.div.div.a["href"]
            except AttributeError:
                pass
            except TypeError:
                pass
            except Exception as e:
                pass
            else:
                final_url = flipkart_url + main_url
                main_url_list.append(final_url)

        allproducts=[]
        for i in range(0,len(main_url_list)):
            page_info=requests.get(main_url_list[i])
            allproducts.append(page_info)

        allproductspagehtml=[]
        for i in range(0,len(allproducts)):
            page_html=bs(allproducts[i].text,"html.parser")
            allproductspagehtml.append(page_html)

        review_box=[]
        for i in range(0,len(allproductspagehtml)):
            info=allproductspagehtml[i].find_all("div",{"class":"_16PBlm"})
            review_box.append(info)

        review_list=[]
        for i in range(0,len(review_box)):
            for j in range(0,len(review_box[i])):
                d={}
                try:
                    comment0=review_box[i][j].div.div.div.find_all("div",{"class":"_3LWZlK _1BLPMq"})
                    d["Ratings"]=comment0[0].text
                    comment1=review_box[i][j].div.div.find_all("p",{"class":"_2-N8zT"})
                    d["Overall"]=comment1[0].text
                    comment2=review_box[i][j].div.div.find_all("div",{"class":"t-ZTKy"})
                    d["Review"]=(comment2[0].text)[:-9]
                    comment3=review_box[i][j].div.div.find_all("p",{"class":"_2sc7ZR"})
                    d["Name"]=comment3[0].text
                    d["Time"]=comment3[1].text
                    comment4=review_box[i][j].div.div.find_all("p",{"class":"_2mcZGG"})
                    comment5=comment4[0].text
                    d["Address"]=comment5[17:]    
                except Exception as e:
                    continue
                else:
                    review_list.append(d)
        
        
        client = pymongo.MongoClient("mongodb+srv://pwskills:pwskills@cluster0.vpmkyl5.mongodb.net/?retryWrites=true&w=majority")
        db = client['review_scrap']
        review = db['review_scrap_data']
        review.insert_many(review_list)

        return render_template('result.html', reviews=review_list)
    
    return("Error")

if __name__=="__main__":
    app.run(host="0.0.0.0")







