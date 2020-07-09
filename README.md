# Simple-WebCrawler
This is a simple web crawler, which takes a URL as an input and will provide below details in a detailed easy readable format.
1. Company Name
2. Company Logo
3. Company Email Address
4. Company Phone Numbers
5. Company Social Profile Links
6. Company Address

This a basic project on how to extract some key and useful insights from a given Domain Name. Using this, we can create much more neat and accurate crawlers for extracting which ever information we need from any given Domain Name.

This project is developed using Streamlit (https://www.streamlit.io/), an open-source framework which we can use to create a simple and neat UI without any HTML, CSS or JavaScript Knowledge. It is the easiest way for data scientists and machine learning engineers to create beautiful, performant apps in only a few hours!  All in pure Python. All for free.

I tried to include all the possible cases to extract the above information, but still for some cases it may fail to extract all the details.

1. Used Regex Patterns for removing all the unwanted characters and for identifying some key phrases. 
2. Used Stop Words from NLTK module to remove stopwords from the html text.
3. Used Pandas to read and query CSV files.
4. Used BeautifulSoup (bs4) module to scrape the domain web pages.

Programming Language: Python3.7

Test the webapp using the given link (https://simplewebcrawler.herokuapp.com/)
