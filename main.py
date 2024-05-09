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
    train_data = train_query.fetchone
    
    if train_data:
        c.execute("DELETE FROM trains WHERE train_number = ? AND departure_date=?", (train_number, departure_date))
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

def categorize_seat(seat_number):
    if(seat_number % 10) in [0, 4, 5, 9]:
        return "Window"
    elif(seat_number % 10) in [2, 3, 6, 7]:
        return "Aisle"
    else:
        return "Middle"
def view_seats(train_number):
    train_query = c.execute(" SELECT * FROM trains WHERE train_number=? ", (train_number, ))
    train_data = train_query.fetchone()
    
    if train_data:
        seat_query = c.execute(f"SELECT 'Number: ' || seat_number, '\n Type:' || seat_type, '\n Name:' || passenger_name, '\n Age:' || passenger_age, '\n Gender:' || passenger_gender as Details, booked FROM seats_{train_number} ORDER BY seat_number asc")
        
        result = seat_query.fetchone()
        
        if result:
            st.dataframe(data=result)

def book_tickets(train_number, passenger_name, passenger_gender, passenger_age, seat_type):
    train_query = c.execute(" SELECT * FROM trains WHERE train_number =? ", (train_number,))
    train_data = train_query.fetchone()
    
    if train_data:
        seat_number = allocate_next_available_seat(train_number, seat_type)
        
        if seat_number:
            c.execute(f"UPDATE seats_{train_number} SET booked=1, seat_type=? , passenger_name=?, passenger_age=?, passenger_gender=? "
                      f"WHERE seat_number=?",(seat_type, passenger_name, passenger_age, passenger_gender))
            conn.commit()
            st.success(f"BOOKED SUCCESSFULLY !!")
            
def allocate_next_available_seat(train_number, seat_type):
    seat_query = c.execute(" SELECT seat_number FROM seat_{train_number} WHERE booked=0 and seat_type=? ""ORDER BY seat_number asc ", (seat_type, ))
    result = seat_query.fetchone()
    
    if result:
        return [0]

def cancel_ticket(train_number, seat_number):
    train_query = c.execute(" SELECT * FROM trains WHERE train_number =? ", (train_number,))
    train_data = train_query.fetchone()
    
    if(train_data):
        c.execute(f'''UPDATE seats_{train_number} SET booked = 0, passenger_name='', passenger_age='', passenger_gender='' WHERE seat_number=?''', (seat_number,))
        conn.commit()
        st.success(f"CANCELLED SUCCESSFULLY !!")

def train_functions():
    st.title("TRAIN ADMINISTRATOR")
    functions = st.sidebar.selectbox("SELECT TRAIN FUNCTIONS",["ADD TRAIN", "VIEW TRAINS", "SEARCH TRAIN", "DELETE TRAIN", "BOOK TICKET", "CANCEL TICKET", "VIEW SEATS"])
    if functions == "ADD TRAIN":
        st.header("Add new train")
        with st.form(key='new_train_details'):
            train_number = st.text_input("Train Number")
            train_name = st.text_input("Train Name")
            departure_date = st.text_input("Date")
            start_destination = st.text_input("Start Destination")
            end_destination = st.text_input("END Destination")
            submitted = st.form_submit_button("ADD TRAIN")
            if submitted and train_name != '' and start_destination != "" and end_destination != "":
                add_train(train_number, train_name, departure_date, start_destination, end_destination)
                st.success("TRAIN ADDED SUCCESSFULLY !!")
    elif functions == "VIEW TRAINS":
        st.title("View Trains")
        train_query = c.execute("SELECT * FROM trains")
        trains = train_query.fetchone()
        
    elif functions == "SEARCH TRAIN":
        st.title("Search Train")
        with st.form(key='search_train_form'):
            train_number = st.text_input("Enter Train Number")
            submitted = st.form_submit_button("SEARCH")
            if submitted:
                train_data = search_train(train_number)
                if train_data:
                    st.success(f"Train Number: {train_data[0]} | Train Name: {train_data[1]} | Start Destination: {train_data[2]} | End Destination: {train_data[3]}")
                else:
                    st.error("Train not found.")
    elif functions == "DELETE TRAIN":
        st.title("Delete Train")
        
        train_number = st.text_input("Enter Train Number")
        departure_date = st.date_input("Enter Departure Date")
        if st.button("DELETE"):
            if train_number and departure_date:
                c.execute(f"DROP TABLE IF EXISTS seat_{train_number}")
                delete_train(train_number, departure_date)
    elif functions == "BOOK TICKET":
        st.title("Book Ticket")
        train_number = st.text_input("Enter Train Number")
        passenger_name = st.text_input("Enter Passenger Name")
        passenger_gender = st.selectbox("Select Passenger Gender", ["Male", "Female", "Other"], index=0)
        passenger_age = st.number_input("Enter Passenger Age", min_value=0, max_value=150, step=1)
        seat_type = st.selectbox("Select Seat Type", ["Window", "Aisle", "Middle"])
        if(st.button("Book Tickets")):
            if train_number and passenger_name and passenger_gender and passenger_age:
                book_tickets(train_number, passenger_name, passenger_gender, passenger_age, seat_type)
    elif functions == "CANCEL TICKET":
        st.title("Cancel Ticket")
        train_number = st.text_input("Enter Train Number")
        seat_number = st.number_input("Enter Seat Number", min_value=1, max_value=50, step=1)
        if st.button("Cancel Ticket"):
            if train_number and seat_number:
                cancel_ticket(train_number, seat_number)
    elif functions == "VIEW SEATS":
        st.title("View Seats")
        
        train_number = st.text_input("Enter Train Number")
        if st.button("VIEW SEATS"):
            if train_number:
                view_seats(train_number)