# -*- coding: utf-8 -*-
"""
Created on Wed Jul 08 02:20:31 2020
@author: Venkata N Divi
"""

import pandas as pd,sys,re,streamlit as st
from DomainInfoExtractor import ExtractInfo

def domainValidity(domain):
    regex = '^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'
    if re.match(regex, domain):
        return True
    else:
        return False
    
def extractData(domainName_):
    result,dInfo = {},ExtractInfo()
    try:
        df = pd.read_csv('CountryStateCodes.csv',sep='\t')
        url = dInfo.getURL(domainName_)
        soup = dInfo.scrapeLink(url)
        
        domain = domainName_ if 'http' in domainName_ else 'http://'+domainName_ 
        domainName = domainName_.replace('www.','').replace('https://','').replace('http://','')
        compName = dInfo.extractCompanyName(domainName_,soup)
        compName = [str(cName, 'utf-8') for cName in compName]
        result['cName'] = list(set(compName))
        
        url = domain if url is None else url
        if soup:
            logo = soup.find('img',id='logo')['src'] if soup.find('img',id='logo') is not None else ''
            filterLinks,logos,contactLink = dInfo.processLinks(soup,url,domainName)
            if len(logo) == 0:
                logo = soup.find('meta',property='og:image')['content'] if soup.find('meta',property='og:image') else soup.find('link',rel='image_src')['href'] if soup.find('link',rel='image_src') else soup.find('meta',itemprop='image')['content'] if soup.find('meta',itemprop='image') else ''
                result['cLogo'] = list(set(logos)) if len(logo) == 0 else [logo]
            else:
                result['cLogo'] = [logo]
                
            mainLinks = [links.strip()[:-1] if links.strip()[-1] == '/' else links.strip() for links in filterLinks]
            mainLinks = [links for links in mainLinks if links.count('/')<=5]
            if len(mainLinks)==0:
                mainLinks.append(url)
            
            filterLinks,socialProfiles = list(set(mainLinks)),[]
            for links in filterLinks:
                try:
                    if 'contact' in links:
                        address,phone = dInfo.extractAddress(links,df)
                        result['Address'] = address  if address and len(address)>0 and 'Address' not in result else [] 
                        result['phone'] = phone  if phone and len(phone)>0 and 'Phone' not in result and len(phone)<=10 else [] 
                            
                    if 'twitter.com' in links or 'linkedin.com' in links or 'facebook.com' in links and links not in socialProfiles:
                        links = links.replace('https://','').replace('http://','').replace('www.','').split('?')[0]
                        socialProfiles.append(links.lower())
                except Exception:
                    pass
            
            if 'Address' not in result:
                url = contactLink if len(contactLink)>0 else url
                address,phone = dInfo.extractAddress(url,df)
                result['Address'] = address  if address and len(address)>0 and 'Address' not in result else [] 
                result['phone'] = phone if phone and len(phone)>0 and 'Phone' not in result and len(phone)<=10 else []
                
            result['SocialProfiles'] = list(set(socialProfiles))
            
        return result
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
        pass
                       
def processDomain():
    st.subheader("**Try the Crawler**")
    domainName_ = st.text_input("Domain Name/URL")
    st.info('**Ex:domain.com or www.domain.com or https://www.domain.com**')
    if st.button('Extract'):
        domName_ = domainName_.replace('https://','').replace('http://','').split('/')[0]
        if len(domName_)<5 or '.' not in domName_ or not domainValidity(domName_):
            st.warning('Please try to enter proper Domain name!!!')
        else:     
            st.success('Crawling '+domainName_+', Please wait!!!')
            result = extractData(domName_)
            st.write(result)
            
def selectOptions():
    try:
        st.write("This is a simple web crawler, which takes a URL as an input and will provide below details in a detailed easy readable format.")
        st.write("""
        - **Company Name**
        - **Company Logo**
        - **Company Email Address**
        - **Company Phone Numbers**
        - **Company Social Profile Links**
        - **Company Address**
        - **Is the given domain is a redirecting to a new domain or not.**""")
        st.write("""This a basic project on how to extract some key and useful insights from a given 
        Domain Name. Using this, we can create much more neat and accurate crawlers for extracting which ever 
        information we needed from any given Domain Name.""")
        st.write("""I tried to include all the possible cases to extract the above information, but still 
        for some cases it may fail to extract all the details.""")
        st.write("""I have used Regex Patterns for removing all the unwanted characters and for identifying 
        some key phrases.""")
        st.subheader('**Use the Left Side Options to test the Service**')
    except Exception as e:
        print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
        
def main():
    st.sidebar.title("Simple Web Crawler")
    st.sidebar.markdown("Try our Service!!!")
    st.sidebar.subheader("Choose")
    activities=["Select","Simple Web Crawler"]
    choice = st.sidebar.selectbox("",activities)
    if choice == 'Select':
        selectOptions()
    elif choice == 'Simple Web Crawler':
        processDomain()
    
if __name__ == '__main__':
    st.write('<!DOCTYPE html><html lang="en">   <head>      <meta charset="UTF-8">      <meta name="viewport" content="width=device-width, initial-scale=1.0">      <meta http-equiv="X-UA-Compatible" content="ie=edge">      <title>Responsive Navigation Bar - W3jar.Com</title>      <style>*,*::before,*::after {  box-sizing: border-box;  -webkit-box-sizing: border-box;}body {  font-family: sans-serif;  margin: 0;  padding: 0;}.container {  height: 80px;  background-color: #052252;  display: -webkit-box;  display: -ms-flexbox;  display: flex;  -ms-flex-wrap: wrap;  flex-wrap: wrap;  -webkit-box-align: center;  -ms-flex-align: center;  align-items: center;  overflow: hidden;}.container .logo {  max-width: 250px;  padding: 0 10px;  overflow: hidden;}.container .logo a {  display: -webkit-box;  display: -ms-flexbox;  display: flex;  -ms-flex-wrap: wrap;  flex-wrap: wrap;  -webkit-box-align: center;  -ms-flex-align: center;  align-items: center;  height: 60px;}.container .logo a img {  max-width: 100%;  max-height: 60px;}@media only screen and (max-width: 650px) {  .container {    -webkit-box-pack: justify;    -ms-flex-pack: justify;    justify-content: space-between;  }  .container .logo {    -webkit-box-flex: 1;    -ms-flex: 1;    flex: 1;  }}.body {  max-width: 700px;  margin: 0 auto;  padding: 10px;} .h1 { color:#FEFEFE; position: center; top: 10px; font-size:135px;font-family:verdana;    margin-top:0px;    margin:0px; line-height:50px; }</style>   </head>   <body>      <div class="container">      <div class="logo">    <a href="#"><img src="https://image.flaticon.com/icons/svg/2344/2344464.svg" alt="logo"></a>    </div> </body></html>', unsafe_allow_html=True)
    st.title("Simple Web Crawler")
    st.markdown("You have a Domain and want to get Key Information from it? **Try our Service!!!**")
    main()