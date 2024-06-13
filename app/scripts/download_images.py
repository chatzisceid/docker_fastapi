import json
import urllib.request
import time

# Your JSON data
data = """
{
   "id": "4v2",
   "images":[
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/2/2b/Berlin_Brandenburger_Tor_um_1900.jpeg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/e/eb/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_02.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/8/84/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_03.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/8/82/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_04.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/b/b5/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_05.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/b/bd/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_06.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/1/1c/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_07.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/2/2b/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_08.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/0/07/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_09.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/d/d6/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_10.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/5/58/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_11.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/49/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_12.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/7/70/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_13.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/6/64/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_14.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/c/c2/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_15.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/a/af/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_16.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/8/82/Wir_haben_es_satt_protest_Berlin_at_Brandenburger_Tor_2024-01-20_17.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/5/5f/Extinction_Rebellion%2C_Besetzung_Brandenburger_Tor.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/42/Brandenburger_Tor_in_Berlin.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/3/39/Brandenburger_Tor_von_lordnikon.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/e/e9/Brandenburger_Tor_Berlin_2005.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/a/af/Brandenburger_Tor_%28Anfang_der_80er%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/3/3c/Brandenburger_Tor_Berlin_2005_4.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/42/Brandenburger_Tor_Berlin_2005_3.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/0/0d/Brandenburger_Tor_Berlin_2005_2.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/4a/Brandenburger_Tor_Berlin_at_night_2023-12-17_01.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/f/f3/Brandenburger_Tor_from_Pariser_Platz_at_night_2023-02-25_01.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/e/ec/Brandenburger_Tor_from_Pariser_Platz_at_night_2023-02-25_02.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/a/a9/Brandenburger_Tor_from_Pariser_Platz_at_night_2023-02-25_03.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/6/66/Conspiracist_protest_Brandenburg_Gate_Berlin_2020-08-28_02.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/5/53/Conspiracist_protest_Brandenburg_Gate_Berlin_2020-08-28_07.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/e/e4/Conspiracist_protest_Brandenburg_Gate_Berlin_2020-08-28_11.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/b/b3/Conspiracist_protest_Brandenburg_Gate_Berlin_2020-08-28_12.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/b/bb/Conspiracist_protest_Brandenburg_Gate_Berlin_2020-08-29_04.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/5/51/Conspiracist_protest_Brandenburg_Gate_Berlin_2020-08-28_14.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/9/9e/Conspiracist_protest_Brandenburg_Gate_Berlin_2020-08-28_22.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/9/9b/BrandenburgerTor.1.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/b/b0/BrandenburgerTor.JPG"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/43/17.Juni.Tafel.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/5/56/Berlin_Brandenburg_Gate_%2828147935004%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/b/b0/Berlin_Brandenburg_Gate_%2828150532233%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/b/bd/Berlin_Brandenburg_Gate_%2828150529023%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/9/98/Berlin_Brandenburg_Gate_%2828688233791%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/f/f9/Berlin_Brandenburg_Gate_%2828660314102%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/40/Berlin_Brandenburg_Gate_%2828481385860%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/1/13/Berlin_Brandenburg_Gate_%2828688307531%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/44/4792_Brandenburg_Gate_July_2019.JPG"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/e/e7/20190722_114814_Brandenburg_Gate_in_July_2019.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/3/3e/Preparation_of_ZDF_new_year_TV_show_at_Brandenburg_gate_2020-12-30_29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/5/5a/Conspiracist_protest_Brandenburg_Gate_Berlin_2020-08-28_10.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/d/d0/Mallory_Weggemann_at_the_Brandenburg_Gate_in_Berlin%2C_2015.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/3/37/Preparation_of_ZDF_new_year_TV_show_at_Brandenburg_gate_2020-12-30_30.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/2/2a/Preparation_of_ZDF_new_year_TV_show_at_Brandenburg_gate_2020-12-30_31.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/d/d0/Brandenburg_Gate_2015_Berlin.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/8/8a/Preparation_of_ZDF_new_year_TV_show_at_Brandenburg_gate_2020-12-30_34.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/7/7f/Preparation_of_ZDF_new_year_TV_show_at_Brandenburg_gate_2020-12-30_33.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/7/79/Preparation_of_ZDF_new_year_TV_show_at_Brandenburg_gate_2020-12-30_32.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/a/a4/Brandenburg_Gate_%28summer_2005%29.JPG"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/5/51/Brandenburg_Gate_2015_01.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/4b/Brandenburg_Gate_2015_02.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/3/30/Brandenburg_Gate_at_night_%28March_2017%29.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/3/3a/Brandenburg_Gate_at_night_-_3.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/8/89/Brandenburg_Gate_at_night_-_2.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/b/b9/Secretary_Kerry_at_the_Brandenburg_Gate.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/3/31/Brandenburg_gate_Berlin_at_night_2022-12-09_02.jpg"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/4/41/BrandenburgGate.JPG"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/2/22/Germany._Berlin_103.JPG"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/c/ca/Germany._Berlin_104.JPG"
      },
      {
         "url":"https://upload.wikimedia.org/wikipedia/commons/0/05/E2K3_BerlinStarbucksGate.jpg"
      }
   ]
}
"""

# Load the JSON data
json_data = json.loads(data)

# Function to download and save an image
def download_image(url, filename):
    urllib.request.urlretrieve(url, filename)

# Iterate over the images in the JSON data
for image in json_data["images"]:
    # Extract the URL and filename (URL path)
    ts = time.time()
    filename = f'/media/chatzise/E0E43345E4331CEA/test/dense/images/{int(ts)}.jpg'    
    # Download and save the image
    download_image(image["url"], filename)
    time.sleep(1)

print("Images downloaded successfully.")
