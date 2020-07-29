# Super Random FTP grabber

Situation:
There is a chance that you may want to download a
sum off files from specific FTP servers, but what
if you just want to download random file collections
from exposed FTP servers online that you're not even
aware of for no apparent reason whatsoever?

This fork of [RandomFtpGrabber](https://github.com/albertz/RandomFtpGrabber) solves this
very specific problem for you!

## Usage

* Configure `config.txt` and enter your desired options and credentials.

    This file contains Shodan-specific configurations.
    
    - `SHODAN_API_KEY` stands for your [account's API key](https://account.shodan.io/).
    - `DORK` stands for the search query. The default query is meant to look up FTP servers that are meant to be accessible to the public.
    - `PAGES` is the amount of pages that this tool will request from Shodan.
    
    Please note that each page stands for 100 individual results (IPs) and using more than 1 page will use one query credit.

* This program stores `*.db` files (e.g. `index.db`) in order to store
  its current state and resume the downloads from where you left it off.

    - If you used this tool recently, you may want to use `--skipShodan` in order to avoid downloading files from the same sources again.

## Specifications

* Python 3.
* Uses the [Shodan](https://shodan.io) (`shodan`) API. (May require membership/subscription)
* Downloads via `wget`.
* Fills out a list of source URLs in the file `./sources.txt`, which you can also extend by yourself.
* Lazy random sampled indexing of the files.
It doesn't build a full index in the beginning, it rather randomly
browses through the given sources and randomly selects files for download.
See [`RandomFileQueue`](https://github.com/albertz/RandomFtpGrabber/blob/master/RandomFileQueue.py)
for details on the random walking algorithm.
If you run it long enough, it still will end up with a full file index, though.
* FTP indexing via Python `ftplib`. HTTP via `urllib3` and `BeautifulSoup`.
* Resumes later on temporary problems (connection timeout, FTP error 4xx),
skips dirs/files with unrecoverable problems (file not found anymore or so, FTP error 5xx).
* Multiple worker threads and a task system with a work queue.
See [`TaskSystem`](https://github.com/albertz/RandomFtpGrabber/blob/master/TaskSystem.py)
for details on the implementation.
* Serializes current state (as readable Python expressions)
and will recover it on restart, thus it will resume all current actions such as downloads.
See [`Persistence`](https://github.com/albertz/RandomFtpGrabber/blob/master/Persistence.py)
for details on the implementation.

## Authors

* Albert Zeyer, [albzey@gmail.com](mailto:albzey@gmail.com).
* Panagiotis Vasilopoulos, hello [@] alwayslivid.com.