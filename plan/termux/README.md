# Automatic Navigation Indicator using Termux
We will be using the fantastic navigation app called [OsmAnd](https://osmand.net/) to have offline navigation and we can display the Indications using our automation as described below.

## Setup Termux

### Install Termux & Termux:API (One time)

### Grant permissions (One time)

### Python setup
Use this [code](./navApi.py)
```bash
pkg install python

# use any directory to setup venv
python -m venv .env
source .env/bin/activate
pip install requests

# copy the above mentioned code
```

---

## Run the Script
Run our `dlNav` android app & start the `Server` which will receive the data from our termux script.

### Start the Termux:API
```bash
termux-api-start
```

### Run automation for automatic indicator lights
```bash
cd <your_venv_path>
source .env/bin/activate

# run code
python navApi.py

# press Ctrl + C to stop the script loop
```
