from openai import OpenAI
import json
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv("keys.env")


def genrate_ai_response(message):
    client = OpenAI(
    api_key=os.getenv("api_key")
    )
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
        {"role": "user", "content": message}
    ]
    )

    return completion.choices[0].message.content
class User:
    def __init__(self,full_name, age, intersets: list,budget, geo_location, visas: list):
        self.full_name = full_name
        self.age = age 
        self.interests = intersets
        self.geo_location = geo_location
        self.visas = visas
        self.budget = budget
        inter = ','.join(intersets)
        msg = f"age is {self.age} , interests: [{inter}] and location is {geo_location}. How kind of travel types will you recommend give me only your recommended travel types (e.g., nature, historical, adventure) seperated by comma without explain anything only travel types seperated by comma"
        recom_ai = genrate_ai_response(msg)
        self.travel_type_recom = recom_ai
    def fetch_recomendation(self,travel_type: str):
        with sqlite3.connect("travel_data.db") as conn:
            cursor = conn.cursor()
            data = cursor.execute("select * from travel_data")
            for row in data:
                if row[1].lower().strip() == travel_type.lower().strip():
                    print(f"id:{row[7]}\nlocation {row[0]}\ntravel_type: {row[1]}\nneeded country visa: {row[2]}\nrating: {row[3]}\ncost: {row[4]}\nseason: {row[5]}\npopularity score: {row[6]}")
                    print("-"*40)
    def optimize_trip_plan(self):
        with sqlite3.connect("travel_data.db") as conn:
            cursor = conn.cursor()
            data = cursor.execute("select * from travel_data")
            recom = [x.lower().strip() for x in self.travel_type_recom.split(',')]
            visas = [x.lower().strip() for x in self.visas]
            for row in data:
                if (row[1].lower().strip() in recom) and int(row[4]) <= self.budget and row[2].lower().strip() in visas:
                    print(f"id:{row[8]}\nlocation {row[0]}\ntravel_type: {row[1]}\nneeded country visa: {row[2]}\nrating: {row[3]}\ncost: {row[4]}\nseason: {row[5]}\npopularity score: {row[6]}")
                    print("-"*40)
    def get_travel_data(self):
        with sqlite3.connect("travel_data.db") as conn:
            cursor = conn.cursor()
            data = cursor.execute("select * from travel_data")
        for row in data:
            print(f"id: {row[7]}\nlocation {row[0]}\ntravel_type: {row[1]}\nneeded country visa: {row[2]}\nrating: {row[3]}\ncost: {row[4]}\nseason: {row[5]}\npopularity score: {row[6]}")
        
    def anlayze_reviews(self,destination_id):
        with sqlite3.connect("travel_data.db") as conn:
            cursor = conn.cursor()
            row = cursor.execute("select * from travel_data where id=?",(destination_id,)).fetchall()[0]
        inter = ','.join(self.interests)
        viasas = ','.join(self.visas)
        user_data = f"[full name:{self.full_name}\nage: {self.age}\ninterests: {inter}\nbudget: {self.budget}\nLocation: {self.geo_location}\ncountry visas this user owns: {viasas}]"
        location_data = f"[id: {row[7]}\nlocation {row[0]}\ntravel_type: {row[1]}\nneeded country visa: {row[2]}\nrating: {row[3]}\ncost: {row[4]}\nseason: {row[5]}\npopularity score: {row[6]}]"
        resp = genrate_ai_response(f"this is users data {user_data} and this is information of the location that this user is choosen would you recommend to visit this please ot not why or hy not with short answer")
        return resp
    def book_visit(self,destination_id,date):
        with sqlite3.connect("travel_data.db") as conn:
            cursor = conn.cursor()
            row = cursor.execute("select * from travel_data where id=?",(destination_id,)).fetchall()[0]
        travels_data_csv = pd.read_csv('travel_data.csv')
        travels_data_csv.loc[len(travels_data_csv)] = [row[0],datetime.datetime.strptime(date,"%Y-%m-%d").strftime("%B")]
        travels_data_csv.to_csv("travel_data.csv",index=False)        
        print("wish you safe and enjoyable journey")
    def get_travel_insights_across_seasons(self,location: str ):
        df=pd.read_csv("travel_data.csv")
        local_df = df[df['location'].str.lower() == location.lower()].groupby('season').agg('count')
        return local_df
    def generate_visual_report(self):
        df=pd.read_csv("travel_data.csv")
        local_df = df.groupby('location').agg('count').reset_index()
        plt.bar(local_df['location'],local_df['season'])
        plt.show()

        
            
            
        
class Travel_Recomendation_sytem:
    def __init__(self):
        self.users = {}
    def generate_user_profile(self,user: User):
        self.users[user.full_name] = {
            'full_name': user.full_name,
            'age': user.age,
            'interests': user.interests,
            'geo_location': user.geo_location,
            'visas': user.visas,
            'budget': user.budget,
            'travel_type_recom': [x.strip() for x in user.travel_type_recom.split(',')]
        }
    def save_to_json(self,filename = "Travel_recom.json"):
        with open(filename, "w") as file:
            json.dump(self.users, file)
    def load_from_json(self,filename = "Travel_recom.json"):
        with open(filename,"r") as file:
            self.users = json.load(file)

travel = Travel_Recomendation_sytem()
# user = User("Ibrohim Pardaboyev",5,['gaming'],3000,'Uzbekistan, Sirdarya',['USA','Germany','Uzbekistan'])
user = User("Yunusbek Pardaboyev",25,['adventure'],1000,'Uzbekistan, Sirdarya',['USA','Germany'])
# travel.generate_user_profile(User("Yunusbek Pardaboyev",25,['adventure'],1000,'Uzbekistan, Sirdarya',['USA','Germany']))
# user.fetch_recomendation("Adventure")
# print(user.anlayze_reviews(0))
# user.visit(0)
# user.book_visit(0,'2025-04-05')
print(user.generate_visual_report())
