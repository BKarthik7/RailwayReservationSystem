import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect('railway.db')
current_page = 'Login or Sign up'
c = conn.cursor()

def create_db():
    
    c.execute("CREATE TABLE IF NOT EXIST users(username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXIST employees (employee_id TEXT, password TEXT, designation TEXT)")
    c.execute("CREATE TABLE IF NOT EXIST Train (train_number TEXT, train_name TEXT, start_destination TEXT, end_destination TEXT)")
    
    create_db()
    
def search_train(train_number):
    
    train_query = c.execute(" SELECT * FROM trains WHERE train_numbers=? ", (train_number,))
    train_data = train_query.fetchone()
    
    return train_data

def train_destination(start_destination, end_destination):
    
    train_query = c.execute(" SELECT * FROM trains where start_destination=? . end_destination=?", (start_destination, end_destination))
    train_data = train_query.fetchone()
    
    return train_data

def add_train(train_number, train_name, departure_date, start_destination, end_destination):
    
    c.execute("INSERT INTO trains (train_number, train_name, departure_date, start_destination, end_destination) values(?, ?, ?, ?, ?)",(train_number, train_name, departure_date, start_destination, end_destination))
    conn.commit()
    create_seat_table(train_number)
    
def delete_train(train_number, departure_date):
    
    train_query = c.execute("SELECT * FROM trains WHERE train_numbers=? ", (train_number,))
    conn.commit()
    st.success(f" TRAIN IS DELETED SUCCESSFULLY ")
    
def create_seat_table(train_number):
    c.execute("CREATE TABLE IF NOT EXISTS seats_{0} ("
              "seat_number INTEGER PRIMARY KEY, "
              "seat_type TEXT, "
              "booked INTEGER, "
              "passenger_name TEXT, "
              "age INTEGER, "
              "passenger_gender TEXT)".format(train_number))

    for i in range(1, 51):
        
        val = categorize_seat(i)
        c.execute(f'''INSERT INTO seats_{train_number} (seat_number, seat_type, booked, passenger_name, age, passenger_gender) VALUES (?, ?, ?, ?, ?, ?);''',(i, val, 0, '', ''))
        
        conn.commit()

def book_tickets(train_number. passenger_name, passenger_gender, passenger_age, seat_type):
        train_query = execute(" SELECT * FROM trains WHERE train_number =?",(train_number))
        train_data = train_query.fetchone()
        