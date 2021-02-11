# Meraki Wireless Health Dashboard

A dashboard that allows flexible filtering of wireless health reporting.

---

The following diagram describes the high-level workflow.

![Meraki Wireless Health Dashboard Overview](./IMAGES/Meraki_Wireless_Health_Dashboard_Overview.png)

![Meraki Wireless Health Dashboard High Level Design](./IMAGES/Meraki_Wireless_Health_Dashboard_High_Level_Design.png)



## Contacts
* Alvin Lau (alvlau@cisco.com)



## Solution Components
* Meraki MR
* Python 3.7



## Prerequisite
- **Meraki - Enable API Access** - enable API and get API key in Meraki Dashboard.
  1. Login to Meraki Dashboard.
  2. Go to "Organization" -> "Settings".
  3. Scroll down to the bottom and check "Enable access to the Cisco Meraki Dashboard API", then click "Save Changes".
  4. Click your email at the top right corner -> "My profile".
  5. Click "Generate new API key", copy your API key in the pop-up window, check the box and click "Done".
  6. Paste and keep the API key in a safe location.



## Installation

1. Clone this repository by `git clone <this repo>`.

2. Optionally, create a Python 3 virtual environment.
```
python3 -m venv venv
source venv/bin/activate
```

3. Install the dependencies.
```
pip install -r requirement.txt
```

4. Run the Flask application.
```
export FLASK_APP=app.py
flask run
```

5. Access the dashboard at http://localhost:5000.



## Run in Docker

1. Clone this repository by `git clone <this repo>`.

2. Go to the root directory containing Dockerfile.

3. Build the container.
```
docker build -t meraki-wireless-health-dashboard .
```

4. Run the container.
```
docker run -d -p 5000:5000 meraki-wireless-health-dashboard
```

5. Access the dashboard at http://localhost:5000.


## License
Provided under Cisco Sample Code License, for details see [LICENSE](./LICENSE)



## Code of Conduct
Our code of conduct is available [here](./CODE_OF_CONDUCT.md)



## Contributing
See our contributing guidelines [here](./CONTRIBUTING.md)
