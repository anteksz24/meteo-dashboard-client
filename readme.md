# Meteo Dashboard Client

Simple Python script to parse and send Vaisala sensor measurements to set API endpoint.

## Description

Script uses watchdog library to monitor latest.txt file and check for new modifications. Script requires SMSAWS message format to be set and Metcast Observation Console to be running.

File content is converted into a list and into a dictionary. Values of certain keys are changed if set in config.json file. New key for timestamp is created, its value is set to current computer date and time or timestamps from text file, in both cases UTC time is used.

Data is sent to set endpoint in a dict, in which value of first key is a dict with measurements, and value of second key is a password.

## Installing and running

Use `pip install -r requirements.txt` to install required packages for the script.

Set `METEO_PASSWORD` environment variable for authentication, exact same password should be set on server.

Choose correct options in config.json file: set replacements if necessary, choose if computer time and date should be used instead of the ones from the file and set correct text file encoding.

Use `python3 main.py <text_file_location> <api_post_method_url>` command to start script. Change arguments to location of latest.txt file, e.g. `C:\Observations\Latest\latest.txt` and API POST method endpoint.