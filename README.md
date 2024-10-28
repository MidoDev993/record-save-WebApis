# record-save WebApis
Captures the APIs of a web page and saves its content

## Install requirements
`pip install -r requirements.txt` or `pipenv install -r requirements.txt`

## How use it
Use the command `mitmproxy -s main.py` (remember to be in the directory where you have the scripts). This will start **mitmproxy** and use the **main.py** script.

1. Enter the URL
2. Enter the time it will be capturing
3. Select the browser (Chrome, Edge, Firefox or the browser you have on your system but that is in the list above).

You can change the IP with `--listen-host [Insert IP]` and the port with `listen_port [Insert port]`.
*For more information about [mitmproxy](https://docs.mitmproxy.org/stable/)*

All files inside the **records** folder are saved in the folder with the name of the URL you placed above. There you will get a list of **requests** and **responses** in a **.db** file.
