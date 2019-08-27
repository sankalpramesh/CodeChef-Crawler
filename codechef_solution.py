import re
import os
import json
import requests
from models import URL
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread

req = requests
handle = ''
codechef_url = 'https://www.codechef.com'
prob_count = 0


def fetching_By_Multiprocess(link):
    global req, handle
    prob = re.search('>(.*)<', link).group(1)

    try:
        print("Fetching the solved {} problem...".format(prob))
        pattern = re.search('/+[\w]+/', link)
        contest = pattern.group(0)[1:-1]
        temp = contest
        if contest == 'status':
            contest = 'Practice'
            temp = ''

        # Make directory of contest folder
        directory_path = handle + "/" + contest
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
            with open("{}/README.md".format(directory_path), "w") as w:
                readme_text = "# " + contest + "\n"
                readme_text += "All my codes submitted at " + URL.BASE + temp
                w.write(readme_text)

        file_path = directory_path + "/" + prob
        if os.path.exists("{}.cpp".format(file_path)):
            return

        next_link = re.search('href="(.*)"', link).group(1)
        next_url = codechef_url + next_link
        resp = req.get(next_url)

        soup = BeautifulSoup(resp.content, 'lxml')
        t = soup.find(href=re.compile("/viewsolution"))

        recall = 0
        while t is None and recall < 5:
            print("Trying Again {}...".format(prob))
            resp = req.get(next_url)
            soup = BeautifulSoup(resp.content, 'lxml')
            t = soup.find(href=re.compile("^/viewsolution"))
            recall += 1
            pass

        if t is None:
            print('Something Went wrong, may be solution of', prob,
                  'is not visible or might be there is some network problem')
            return

        # Forward request to the solution
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) \
                                   AppleWebKit/537.11 (KHTML, like Gecko) \
                                   Chrome/23.0.1271.64 Safari/537.11'}
        resp_final = req.get(codechef_url + t['href'],
                             headers=headers, stream=True)
        soup = BeautifulSoup(resp_final.content, 'lxml')

        # Find JSON Script
        data = soup.find("div", class_="ns-content")
        soup = BeautifulSoup(str(data), 'lxml')
        data = soup.find("script")

        # If JSON Script is not found
        if data is None:
            print('Script not found')
            return

        # If JSON Script is found store in dictionary
        json_dict = str(data.contents[0]).split(" meta_info = ")[-1]
        json_dict = json_dict.strip()[:-1]
        info = json.loads(json_dict)

        # Make file of problem solution
        with open("{}.{}".format(file_path,
                                 info['data']['languageExtension']), "w") as w:
            prob_link = URL.BASE + temp + "problems/" + prob
            header = "// " + prob_link + "\n\n"
            w.write(header)
            w.flush()

            code = info['data']['plaintext']
            if (type(code) == bytes):
                code = code.decode('utf-8')
            w.write(code)

        print("Successfully Downloaded {}".format(prob))
        global prob_count
        prob_count += 1

    except requests.exceptions.RequestException as e:
        print("Error occured in {} -> {}" .format(prob, e))
        return


# Thread worker used to synchronise the thread parallely
task_queue = Queue()


def worker():
    while not task_queue.empty():
        address = task_queue.get()
        fetching_By_Multiprocess(address)
        task_queue.task_done()


def codechef_download(request, handle_name):
    global req, handle
    req, handle = request, handle_name
    print('Please be patient, Your codes are downloading')

    url = URL.BASE + '/users/' + handle

    if not os.path.exists(handle):
        os.mkdir(handle)
        with open("{}/README.md".format(handle), "w") as w:
            readme_text = "# " + "CODECHEF\n"
            readme_text += "All my codes Submitted and Accepted by " + url
            w.write(readme_text)

    try:
        r = req.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        t = soup.find('section', class_='rating-data-section problems-solved')
        link = t.findAll('a')

        Links = []
        for x_link in link:
            Links.append(str(x_link))

        NUM_WORKERS = 1
        threads = [Thread(target=worker) for _ in range(NUM_WORKERS)]
        [task_queue.put(item) for item in Links]
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
        global prob_count
        print('Total codes downloaded:', prob_count)
    except:
        print("Something might went wrong! Please check your Internet connection")


if __name__ == '__main__':
    handle = ''  # Write down your handle name
    codechef_download(requests, handle)
