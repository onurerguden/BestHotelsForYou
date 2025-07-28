import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from bs4 import BeautifulSoup
import requests
import pandas as pd
from PIL import Image, ImageTk
import io
from datetime import datetime

def scrapeHotels(city, check_in, check_out, currency):
    url = f'https://www.booking.com/searchresults.html?ss={city}&checkin={check_in}&checkout={check_out}&selected_currency={"EUR"}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"An Error Appears:")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    hotels = soup.find_all('div', {'data-testid': 'property-card'})

    if not hotels:
        return []

    hotelsData = []

    for hotel in hotels:
        name_element = hotel.find('div', {'data-testid': 'title'})
        name = name_element.text.strip() if name_element else "EMPTY_DATA"

        address_element = hotel.find('span', {'data-testid': 'address'})
        address = address_element.text.strip() if address_element else "EMPTY_DATA"

        distance_element = hotel.find('span', {'data-testid': 'distance'})
        distance = distance_element.text.strip() if distance_element else "EMPTY_DATA"

        score_element = hotel.find('span', {'class': 'a3332d346a'})
        score = score_element.text.strip() if score_element else "EMPTY_DATA"

        price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        price_text = price_element.text.strip() if price_element else "PRICE_NOT_FOUND"

        try:
            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
        except ValueError:
            price = 0.0

        if currency == "TRY":
            price = price * 30

        image_element = hotel.find('img', {'data-testid': 'image'})
        image_url = image_element['src'] if image_element else None

        hotelsData.append({'NAME': name, 'ADDRESS': address, 'DISTANCE': distance, 'SCORE': score, 'PRICE': price, 'IMAGE_URL': image_url})

    sortedHotels = sorted(hotelsData, key=lambda x: x['PRICE'])
    return sortedHotels

def saveCsv(data):
    df = pd.DataFrame(data).drop(columns=['IMAGE_URL'])
    df.to_csv('myhotels.csv', index=False)

def validateDates(check_in, check_out):
    if check_in == check_out:
        return False

    check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
    delta = check_out_date - check_in_date

    if delta.days > 365:
        messagebox.showerror("Error", "The stay duration should be less than or equal to 365 days.")
        return False

    return check_in <= check_out

def searchHotels():
    city = city_var.get()
    if not city:
        error_label.config(text="Please select a city")
        return

    check_in = checkin_var.get()
    check_out = checkout_var.get()
    currency = currency_var.get()

    if not validateDates(check_in, check_out):
        error_label.config(text="Check-out date should be after check-in date")
        return

    hotels_data = scrapeHotels(city, check_in, check_out, currency)
    if hotels_data:
        saveCsv(hotels_data)
        showResults(hotels_data[:5])
    else:
        error_label.config(text="No hotels found or there was an error retrieving data.")

def showResults(hotels_data):
    result_window = tk.Toplevel(root)
    result_window.title("Search Results")

    headers = ["Hotel Title", "Hotel Address", "Distance to City Center", "Hotel Ranking", "Price", "Image"]
    for i, header in enumerate(headers):
        tk.Label(result_window, text=header, font=('Calibri', 12, 'bold')).grid(row=0, column=i, padx=5, pady=5)

    for i, hotel in enumerate(hotels_data):
        for j, (key, value) in enumerate(hotel.items()):
            if key == 'PRICE':
                value = f"{value} {currency_var.get()}"
            if key == 'IMAGE_URL' and value:
                response = requests.get(value)
                image_data = response.content
                image = Image.open(io.BytesIO(image_data))
                image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)
                label = tk.Label(result_window, image=photo)
                label.image = photo
                label.grid(row=i + 1, column=j, padx=5, pady=5)
            else:
                tk.Label(result_window, text=value, font=('Calibri', 10)).grid(row=i + 1, column=j, padx=5, pady=5)

def highlight(event):
    event.widget.config(background="lightblue")

def unhighlight(event):
    event.widget.config(background="white")

root = tk.Tk()
root.title("Best Hotels for You")
root.configure(bg='white')
root.geometry('800x600')


top_frame = tk.Frame(root, bg='red', height=45)
top_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(top_frame, text="Best Hotels ForYou", font=('Calibri', 80, 'bold'), fg='white', bg='red').place(relx=0.5, rely=0.5, anchor=tk.CENTER)

bottom_frame = tk.Frame(root, bg='white')
bottom_frame.pack(fill=tk.BOTH, expand=True)

developer_label = tk.Label(root, text="Developed by Onur Ergüden", font=('Calibri', 10), bg='white')
developer_label.pack(side=tk.BOTTOM, padx=10, pady=10)

left_frame = tk.Frame(bottom_frame, bg='white')
left_frame.grid(row=1, column=0, pady=20)

city_label = ttk.Label(left_frame, text="Select City:", font=('Calibri', 12))
city_label.grid(row=0, column=0, pady=5)

city_var = tk.StringVar()
city_dropdown = ttk.Combobox(left_frame, textvariable=city_var,
                             values=["Paris", "Rome", "Berlin", "London", "Barcelona", "Amsterdam", "Vienna", "Prague","Madrid", "Florence", "New York", "Los Angeles", "San Francisco", "Chicago","Miami", "Tokyo", "Beijing", "Shanghai", "Hong Kong", "Singapore", "Bangkok","Dubai", "Sydney", "Melbourne", "Cape Town", "Moscow", "Toronto", "Vancouver","Buenos Aires", "Rio de Janeiro", "Istanbul", "Seoul", "Mumbai", "Mexico City","Kuala Lumpur", "Lisbon", "Dublin", "Cairo", "Johannesburg"])
city_dropdown.grid(row=0, column=1, pady=5)

city_dropdown.bind("<Enter>", highlight)
city_dropdown.bind("<Leave>", unhighlight)

checkin_label = ttk.Label(left_frame, text="Check-in Date:", font=('Calibri', 12))
checkin_label.grid(row=1, column=0, pady=5)
checkin_var = tk.StringVar()
checkin_calendar = DateEntry(left_frame, textvariable=checkin_var, date_pattern='yyyy-mm-dd')
checkin_calendar.grid(row=1, column=1, pady=5)

checkout_label = ttk.Label(left_frame, text="Check-out Date:", font=('Calibri', 12))
checkout_label.grid(row=2, column=0, pady=5)
checkout_var = tk.StringVar()
checkout_calendar = DateEntry(left_frame, textvariable=checkout_var, date_pattern='yyyy-mm-dd')
checkout_calendar.grid(row=2, column=1, pady=5)

currency_label = ttk.Label(left_frame, text="Select Currency:", font=('Calibri', 12))
currency_label.grid(row=3, column=0, pady=5)
currency_var = tk.StringVar(value="EUR")
euro_radio = ttk.Radiobutton(left_frame, text="Euro (EUR)", variable=currency_var, value="EUR")
euro_radio.grid(row=3, column=1, pady=5, sticky="w")
try_radio = ttk.Radiobutton(left_frame, text="Turkish Lira (TRY)", variable=currency_var, value="TRY")
try_radio.grid(row=4, column=1, pady=5, sticky="w")

search_btn = ttk.Button(left_frame, text="Search", command=searchHotels)
search_btn.grid(row=5, columnspan=2, pady=10)

error_label = ttk.Label(left_frame, text="", font=('Calibri', 12), foreground='red')
error_label.grid(row=6, columnspan=2, pady=10)

root.mainloop()
