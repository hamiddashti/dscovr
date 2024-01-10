import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL of the webpage
url = "https://asdc.larc.nasa.gov/data/DSCOVR/EPIC/L2_VESDR_02/2016/08/"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the webpage
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all anchor (a) tags with an href attribute
    links = soup.find_all('a', href=True)

    # Extract and print the file names
    for link in links:
        # Join the base URL with the relative URL to get the complete URL
        file_url = urljoin(url, link['href'])
        # Extract the file name from the URL
        file_name = file_url.split("/")[-1]
        print(file_name)

else:
    # Print an error message if the request was not successful
    print(f"Error: Unable to fetch the webpage. Status code: {response.status_code}")
