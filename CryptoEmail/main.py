import requests
import lxml.html as lh
import pandas as pd
from IPython.display import display
import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

# Setup Pandas
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
# Get environment variables
USER = os.environ.get('GMAIL_USER')
PASSWORD = os.environ.get('GMAIL_PASS')
url = 'https://www.coingecko.com/en/coins/recently_added'
# Create a handle, page, to handle the contents of the website
page = requests.get(url)
# Store the contents of the website under doc
doc = lh.fromstring(page.content)
# Parse data that are stored between <tr>..</tr> of HTML
tr_elements = doc.xpath('//tr')
list = [len(T) for T in tr_elements[:12]]
my_elem = doc.xpath('//tr')
# Create empty list
col = []
i = 0
# For each row, store each first element (header) and an empty list
for t in my_elem[0]:
    i += 1
    name = t.text_content()
    name = name.strip()
    name = name.replace('\n', '')
    col.append((name, []))
for j in range(1, len(tr_elements)):
    # T is our j'th row
    T = tr_elements[j]
    # If row is not of size 10, the //tr data is not from our table
    if len(T) != 12:
        break
    # i is the index of our column
    i = 0
    # Iterate through each element of the row
    for t in T.iterchildren():
        data = t.text_content()
        # Check if row is empty
        data = data.strip()
        data = data.replace('\n', '')
        if i > 0:
            # Convert any numerical value to integers
            try:
                data = int(data)
            except:
                pass
        # Append the data to the empty list of the i'th column
        col[i][1].append(data)
        # Increment i for the next column
        i += 1
Dict = {title: column for (title, column) in col}
df = pd.DataFrame(Dict)
df = df[['Coin', 'Price', 'Last Added']]
display(df)

df.to_excel("Crypto.xlsx", sheet_name='Current_Crypto')
msg = EmailMessage()
subject = 'Current Cryptos'
body = df
text = "Attached is your daily update of the most recent cryptos."
msg['From'] = USER
## msg['To'] = '' ### This line is used to send the email to someone, uncomment it to send it
msg['Date'] = formatdate(localtime=True)
msg['Subject'] = subject
msg.set_content(text)

with open('Crypto.xlsx', 'rb') as f:
    file_data = f.read()
    file_type = 'xlsx'
    file_name = f.name

msg.add_attachment(file_data, maintype='Spreadsheet', subtype=file_type, filename=file_name)


with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.connect("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(USER, PASSWORD)
    smtp.send_message(msg)
