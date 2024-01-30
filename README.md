# milliyet-archive
This script is used to fetch data from the Milliyet Newspaper Archive (https://gazetearsivi.milliyet.com.tr) based on a specific date input by the user.

How it works
The script first checks if a directory named 'images' exists in the current working directory. If it doesn't, it creates one.

It then prompts the user to input a date in the format 'YYYY.MM.DD'. The script checks if the input is in the correct format. If it isn't, it raises a ValueError.

The script then constructs a URL using the input date and sends a GET request to the Milliyet Newspaper Archive. The headers for the request are predefined in the script.

# Dependencies
This script requires the following Python libraries:

requests: Used to send the HTTP request.
re: Used for regular expressions.
os: Used for interacting with the operating system.
img2pdf: Used for converting images to PDF.
datetime: Used for date and time operations.
Usage
To use this script, simply run it in a Python environment. When prompted, input a date in the 'YYYY.MM.DD' format. The script will then fetch data from the Milliyet Newspaper Archive for that date.

