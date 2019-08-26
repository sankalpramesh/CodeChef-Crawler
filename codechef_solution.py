import requests, re, os
from bs4 import BeautifulSoup
from Queue import Queue
from threading import Thread
import json
from time import sleep
from models import URL
import urllib   
req = requests
handle = ''
codechef = 'https://www.codechef.com'
prob_count = 0

def fetching_By_Multiprocess(link):
  global req, handle
  prob = re.search('>(.*)<', link).group(1)
  try:
    print("Fetching the solved {} problem...".format(prob))
    pat = re.search('/+[\w]+/',link)
    contest = pat.group(0)
    ############################################################################
    temp = contest
    ############################################################################
    if contest == '/status/':
      contest = '/Practice/'
      ############################################################################
      temp = ''
      ############################################################################

    # Make directory of contest folder
    if not os.path.exists(handle + '/' + contest):
      os.makedirs(handle + contest)
      #
      w1 = open( handle + contest + "README.md" , 'w' )
      readme_text = "# " + contest[1:-1] + "\n" + "All my codes submitted at " + URL.BASE + temp 
      w1.write(readme_text) 
      #

    next_link = re.search('href="(.*)"', link).group(1)
    nxt_url = codechef + next_link    
    rqt = req.get(nxt_url)    
    soup = BeautifulSoup(rqt.content,'lxml')
    t = soup.find(href=re.compile("/viewsolution"))
    recall = 0
    while  t == None and recall < 3:
      print("Trying Again {}...".format(prob))
      rqt = req.get(nxt_url)
      soup=BeautifulSoup(rqt.content, 'lxml')
      t = soup.find(href=re.compile("^/viewsolution"))
      recall += 1
      pass
    
    if t == None:
      print('Something Went wrong, may be solution of',prob,'is not visible or might be there is some network problem')
      return

    #Forward request to the solution
    headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    rqt_final = req.get(codechef+t['href'],headers=headers,stream=True)
    soup = BeautifulSoup(rqt_final.content,'lxml')
    
    # Find language
    lang=soup.find('pre')
    #print(lang.contents[0])
        # If language is not found, download in .text file
    if lang == None:
      w = open(handle + contest+ prob + '.text')
      code = soup.find('div', id='solutiondiv')
      w.write(code.text)
      print('Language not found,Successfully downloaded in .text file')
      return
    lang2=json.loads(str(lang.contents[0]))
    #print(lang2)
    w = open(handle + contest + prob + '.' + lang2['data']['languageExtension'], 'w')
    
    code=lang2['data']['plaintext']
    ############################################################################
    matter = urllib.unquote(code).decode('utf8')
    prob_link = URL.BASE + temp + "problems/" + prob 
    matter = "// " + prob_link + "\n\n" + matter 

    w.write( matter ) 
    #############################################################################

    #w.write(urllib.unquote(code).decode('utf8'))
    
    print("Successfully Downloaded {}" .format(prob))
    global prob_count
    prob_count += 1
  except requests.exceptions.RequestException as e:
    print("Error occured in {} -> {}" .format(prob, e))
    return 

# Thread worker used to synchronise the thread parallely
task_queue = Queue()
def worker():
    while task_queue.empty() == False:
        address = task_queue.get()
        fetching_By_Multiprocess(address)
        task_queue.task_done()

def codechef_download(request, Handle_name):
  global req, handle
  req, handle = request, Handle_name
  print('Please be patient, Your codes are downloading')
  
  url = URL.BASE + '/users/' + handle

  if not os.path.exists(handle):
   os.makedirs(handle)
   ############################################################################
   w2 = open ( handle + "/README.md" , 'w' )
   readme_text1 = "# " + "CODECHEF\n" + "All my codes Submitted and Accepted at " + url 
   w2.write(readme_text1)
   ############################################################################

  
  try:
      r = req.get(url)
      soup=BeautifulSoup(r.content, 'lxml')

      t = soup.find('section', class_ = 'rating-data-section problems-solved')
      link = t.findAll('a')
      Links = []
      for x_link in link:
        Links.append(str(x_link))
      NUM_WORKERS = 1
      threads = [Thread(target = worker) for _ in range(NUM_WORKERS)]
      [task_queue.put(item) for item in Links]
      [thread.start() for thread in threads]
      [thread.join() for thread in threads]
      global prob_count
      print ('Total codes downloaded:', prob_count)
  except:
    print("Something might went wrong! Please check your Internet connection")
 

if __name__ == '__main__':
  handle = '' #Write down your handle name
  codechef_download(requests, handle)

