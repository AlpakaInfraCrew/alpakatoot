# megaretoot

Script to automatically re-toot/boost toots from your followers using a given hashtag.

Inspired by superretoot: https://github.com/chaostreff-flensburg/superretoot

## Installation

```
git clone https://github.com/Eigenbaukombinat/megaretoot.git
cd megaretoot
python3 -m venv .
bin/pip install -r requirements.txt
```

## Configuration

```
cp config.py.example config.py
```

Edit config.py to your needs.

## First run

In case you want to ignore all matching toots from the past, run with `--dry` first, if you want to explicitly boost one matching toot per account, even from the past, you can do so by using `--force` on the first run. 

```
bin/python megaretoot.py [ --dry | --force ]
```

## Run it regularly

Add a cronjob to run the script every 5 minutes.

```
*/5 * * * * cd /path/to/your/checkout  && bin/python megaretoot.py >/dev/null 2>&1
```


