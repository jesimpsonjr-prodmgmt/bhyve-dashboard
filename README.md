# B-Hyve Irrigation Dashboard

A self-hosted web dashboard for controlling Orbit B-Hyve smart sprinkler systems on your local network.

![Dashboard Preview](screenshot.png)
<img width="1421" height="863" alt="image" src="https://github.com/user-attachments/assets/96c88ab9-01a5-41ca-832a-07500a99176c" />


## Features

- **Real-time Device Status** - Connection state, WiFi signal strength, battery level, firmware version
- **Zone Controls** - Start/stop individual zones with adjustable duration (3-30 minutes)
- **Active Watering Display** - Live countdown timer with one-click stop
- **Schedule Management** - View programs, next run times, enable/disable schedules
- **Rain Delay** - Set 24/48/72 hour delays or clear existing delays
- **Weather Integration** - Current conditions, humidity, wind, precipitation chance
- **Smart Features Status** - Smart watering, freeze protection, weather adjustment indicators
- **Watering History** - Recent activity log with zone, duration, and water usage

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **API:** Orbit B-Hyve Cloud API (unofficial/reverse-engineered)

## Requirements

- Python 3.8+
- Orbit B-Hyve account with registered device(s)
- Network access to Orbit's cloud API

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jesimpsonjr-prodmgmt/bhyve-dashboard.git
cd bhyve-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python bhyve_server.py
```

4. Open your browser to `http://localhost:5678`

5. Log in with your Orbit B-Hyve credentials

## Configuration

The server runs on port `5678` by default. To change this, edit the last line in `bhyve_server.py`:

```python
app.run(host='0.0.0.0', port=YOUR_PORT, debug=False)
```

## Screenshots

### Dashboard Overview
<img width="1415" height="861" alt="image" src="https://github.com/user-attachments/assets/90bcaf2b-6d1d-44b6-92c7-f79eeef18892" />


## Security Notes

- Credentials are stored in memory only (not persisted to disk)
- Designed for LAN use behind a firewall
- All communication with Orbit uses HTTPS
- For production use, consider adding authentication middleware

## Disclaimer

This project uses an unofficial, reverse-engineered API and is not affiliated with or endorsed by Orbit Irrigation Products, Inc. The API may change without notice, which could break functionality. Use at your own risk.

## Built With

This project was built with AI assistance using [Claude](https://claude.ai) by Anthropic.

## License

MIT License - feel free to use, modify, and distribute.

## Acknowledgments

- [pybhyve](https://github.com/sebr/pybhyve) - Python library that helped inform the API structure
- [bhyve-home-assistant](https://github.com/sebr/bhyve-home-assistant) - Home Assistant integration reference
