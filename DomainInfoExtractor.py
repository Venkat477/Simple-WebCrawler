# -*- coding: utf-8 -*-
"""
Created on Wed Jul 08 02:20:31 2020
@author: Venkata N Divi
"""

from re import sub
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from html.parser import HTMLParser
import requests,sys,re,urllib.parse,unicodedata,urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

stop = [word for word in set(stopwords.words('english')) if len(word)>1]
regexPhone = re.compile(r"\+?\d[\d -]{8,12}\d")
regexZipCode = re.compile(r"(\b\d{5}-\d{4}\b|\b\d{5}\b|\b\d{6}\b|\b\d{3}[-\s]\d{3}\b)")

peopleStops = ['staff','people','hall','contact','employee','leadership','team','directory','about','dept','our','management']
spLinks = ['twitter.com','linkedin.com','facebook.com']
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"
types = ['.png','.jpg','.jpeg','.pdf','.doc','.txt','.docx','.xml','.json','/search/','/comments/','/archive','/node/','.mp','/files/','/checkout/','/white-paper-pdf/','/downloads/','/user/','/category/','/alphabet']

class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        matchTaggers = ['p','h1','h2','h3','h4','h5','h6','a','br','label','div','span']
        if tag in matchTaggers:
            self.__text.append('\n\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')
    
    def text(self):
        return ''.join(self.__text).strip()

class ExtractInfo():
    def __init__(self):
        print ("init") 
        
    def scrapeLink(self,url):
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"
        try:
            headers = {'User-Agent': user_agent}
            response = requests.get(url, headers=headers, verify=False, timeout=(15, 20))
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
        
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            pass
    
    def dehtml(self,text):
        try:
            parser = _DeHTMLParser()
            parser.feed(text)
            parser.close()
            return parser.text()
        except:
            return text
        
    def extractPhoneNumbers(self,sentence):
        try:
            phone1 = []
            for text in sentence.split('\n'):
                text = text.replace(')','').replace('(','').replace('.','')
                if len(text)>0:
                    word = text.strip()
                    matches = re.findall(regexPhone, word)
                    if matches:
                        for match in matches:
                            match = match.replace('-','').replace('(','').replace(')','').replace('+','').strip()
                            if match not in phone1:
                                phone1.append(match)
            
            if len(phone1)>0:
                return phone1
            else:
                return None
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return None
        
    def extractZipCode(self,sentence):
        try:
            zip1 = []
            for text in sentence.split('\n'):
                text = text.replace(',',' ').strip()
                if len(text)>0:
                    mainText = ''
                    for txt in text.split():
                        mainText += txt[:-1] if txt[-1] == '.' else txt
                        mainText += ' '
                        
                    if '+' not in mainText and '(' not in mainText and '.' not in mainText and '#' not in mainText:
                        word = mainText.strip()
                        matches = re.findall(regexZipCode, word)
                        if matches:
                            for match in matches:
                                if match not in zip1:
                                    zip1.append(match)
            
            if len(zip1)>0:
                return zip1
            else:
                return None
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return None
        
    def getCityStateNames(self,zipCode):
        headers,finalResult = ['Place','Zip','Country','State','City','Place1'],[]
        try:
            url = 'https://www.geonames.org/postalcode-search.html?q='+str("".join(zipCode.split())).replace(' ','')+'&country='
            soup = self.scrapeLink(url)
            if soup is not None and soup.find('table',class_='restable'):
                data = soup.find('table',class_='restable').findAll('tr')[1:]
                for dd in data:
                    if len(dd.find_all('td'))>3:
                        result = {}
                        for head,td in zip(headers,dd.find_all("td")[1:]):
                            data = td.get_text().replace('\n','')
                            result[head] = data.encode('utf-8')
                            
                        finalResult.append(result)
            
            return finalResult
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return finalResult
    
    def getStateCodes(self,country,state,df):
        try:
            df1 = (df.loc[(df['Country'] == country) & (df['StateName'] == state)])
            stateCode = df1['StateCode'].tolist()
            if stateCode and len(stateCode)>1:
                return stateCode[0]
            else:
                return None
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return None
                    
    def getMatchedSen(self,zip1,sentences,finalTextSplitter,df):
        addresses = []
        try:
            for zipCode in zip1:
                zipCode = zipCode.split('-')[0] if '-' in zipCode else zipCode
                result = self.getCityStateNames(zipCode)
                for res in result:
                    try:
                        country,city,state,place,place1 = res['Country'].decode('utf-8'),res['City'].decode('utf-8'),res['State'].decode('utf-8'),res['Place'].decode('utf-8'),res['Place1'].decode('utf-8')
                        stateCode = self.getStateCodes(country,state,df)
                        for sen in sentences:
                            sen1 = sen.replace(' '+stateCode+' ',' '+state+' ') if stateCode and ' '+stateCode+' ' in sen else sen
                            if (len(country)>1 and country in sen1) or (len(city)>1 and city in sen1) or (len(state)>1 and state in sen1) or (len(place)>1 and place in sen1) or (len(place1)>1 and place1 in sen1):
                                if zipCode in sen:
                                    index,commaCount = finalTextSplitter.index(sen),sen.count(',')
                                    address = finalTextSplitter[index-1]+','+sen1 if commaCount == 1 else sen1
                                    addresses.append(address)
                    
                    except Exception as e:
                        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception,e)
                        pass
                    
            return addresses
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return addresses
    
    def getURL(self,domain):
        url = domain if 'http' in domain else 'http://'+domain 
        try:
            response = requests.get(url, headers={'User-Agent': user_agent}, verify=False, timeout=(15, 20))
            if response and response.history:
                redirectURL = response.url
                url = urllib.parse.urljoin(redirectURL, '/')
            
            return url
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return url
        
    def processLinks(self,soup,url,domain):
        try:
            contactLink = ''
            if soup:
                links,images = soup.find_all('a', href = True),soup.find_all('img', src = True)
                for link in links:
                    if 'contact' in link.text.lower():
                        contactLink = urllib.parse.urljoin(url, link['href'])
                        break
                        
                links = [urllib.parse.urljoin(url, link['href']) for link in links]
                logolinks = [urllib.parse.urljoin(url, link['src']) for link in images]
                logos = [link for link in logolinks if 'logo' in link]
                
                socialProfiles = [link for stt in spLinks for link in links if stt in link]
                domainLinks = list(set([link for link in links if domain in link and 'http' in link and not any(type1 in link for type1 in types)]))
                domainLinks = [link[:-1] if link.strip()[-1] == '/' else link for link in domainLinks ]
                filterLinks = [link for link in domainLinks if any(linkwords in peopleStops for linkwords in re.split("[^a-zA-Z0-9\s]",link.split('/')[-1]))]
                
                return list(set(filterLinks+socialProfiles)),logos,contactLink
            else:
                return [url],[],contactLink
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return [url],[],contactLink
    
    def extractAddress(self,url,df):
        soup,address = self.scrapeLink(url),[]
        try:
            for script in soup(["script", "style"]):
                script.extract()    
                        
            text,finalText = self.dehtml(str(soup)),''
            for splitter in text.split('\n'):
                if len(splitter)>0:
                    processText11 = ' '.join(word for word in splitter.split() if word.lower() not in stop)
                    finalText = finalText+processText11.strip()+'\n'
            
            finalTextSplitter = finalText.split('\n')
            phone = self.extractPhoneNumbers(finalText)
            zip1 = self.extractZipCode(finalText)
            if zip1:
                sentences = list(set([text for zipCode in zip1 for text in finalTextSplitter if zipCode in text]))
                address = self.getMatchedSen(zip1,sentences,finalTextSplitter,df)
            
            return list(set(address)),phone
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return address,[]
    
    def extractCompanyName(self,dom,soup):
        cNames = []
        try:
            dom = dom.split('www.')[1] if 'www.' in dom else dom
            #url = dom if 'http' in dom else 'http://'+dom.strip()
            if soup is not None:
                title = soup.find('title')
                metas = soup.find('meta',property='og:site_name')
                if metas:
                    cNames.append(unicodedata.normalize('NFKD', metas['content'].replace('\n','').replace('\r','').replace('\t','').strip()).encode('ascii','ignore'))
                if title and len(cNames)==0:
                    cNames.append(unicodedata.normalize('NFKD', title.text.replace('\n','').replace('\r','').replace('\t','').strip()).encode('ascii','ignore'))
        
            return cNames
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno),Exception, e)
            return cNames