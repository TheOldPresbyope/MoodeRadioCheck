# moOdeRadioCheck

This repo contains a Python script radiocheck.py which checks that streaming audio URLs and PLS files containing them are playable.

The original purpose of this script was to ease the task of checking the 150+ curated radio station "presets" which are included in each release of the [moOde audio player](http://moodeaudio.org). It does this by asking the [Music Player Daemon](https://www.musicpd.org) (MPD) component to play each PLS file for 0.5s and reading the return code. The script will not start its own MPD process; it checks first that the moOde player is already running an MPD process.

Over time the script has grown like a mushroom to allow checking

* a single streaming audio URL
* a streaming audio URL contained in a single PLS file
* streaming audio URLs contained line-by-line in a text file
* streaming audio URLs contained in PLS files found in a given directory and its subdirectories
* streaming audio URLs contained in PLS files found in the moOde RADIO directory and its subdirectories.

Although it is convention to use the .pls extension to denote a PLS file, this script does not require it. Rather, the Linux _file_ command is used to identify candidate PLS files. Almost no meaningful syntactic or semantic checking of the PLS file is done other than requiring the presence of the File1=\<URL> and Title1=\<Station name> lines. PLS files whose File1= line identify a local media file rather than a streaming audio URL are skipped.

Since this script uses the MPD instance running in the moOde player, it exercises the moOdeUI playback screen, making for an interesting slide show. A scan of the moOde RADIO directory will take over a minute to complete.

WARNING: This script sets the moOde volume to 0 to try to protect the user's system, but this has no effect if volume control is disabled.

Notes:
* A streaming audio URL may fail to play temporarily due to issues at the server or in an intervening gateway or, generally, the content delivery network.
* Geofenced URLs will fail for outsiders.
* Just because MPD says it can play a URL doesn't mean the source is streaming useful audio.
* Subdirectories are including in directory checks because I have sorted my moOde radio stations into subdirectories by genre.
* Python 3.6 or above is required (moOde 6.4.2 is already at 3.7.3)
* one could imagine extending this script, for example, to start its own MPD process or to use the MPD process on a remote moOde player. Not hard to do but seems totally unnecessary.

## Usage

Download the radiocheck.py file to somewhere convenient, for example, user pi's home directory. Make sure the script is executable, e.g.,

`chmod +x radiocheck.py`

Here is the script's help output
```
pi@moode:~ $ ./radiocheck.py -h
usage: radiocheck.py url|file|dir|RADIO|-h

check mpd can play a given url, or the url in a given pls file, or the urls
contained line-by-line in a given file, or the url in every pls file in a
given dir and below, or ('RADIO') the url in every pls file in the moOde RADIO
directory and below

positional arguments:
  arg         url|file|dir|RADIO

optional arguments:
  -h, --help  show this help message and exit

NOTES: 1) protect spaces in filename, 2) mpd process must be running
```
___
## Examples

### A single URL
```
pi@moode:~ $ ./radiocheck.py http://radionz-ice.streamguys.com:80/national.mp3
http://radionz-ice.streamguys.com:80/national.mp3 is a playable url
```

### A single PLS file
```
pi@moode:~ $ ./radiocheck.py sdf.pls
sdf.pls is a playable pls file
```
### URLs in a file
```
pi@moode:~ $ ./radiocheck.py myURL.list
mpd: Failed to decode http://199.189.87.9:10999/mp3-320; CURL failed: The requested URL returned error: 404 File Not Found

mpd: Failed to decode http://stream1.megarockradio.net:8240/; CURL failed: The requested URL returned error: 404 File Not Found

mpd: Failed to decode http://stream.radioactive.fm:8000/ractive; CURL failed: Failed to connect to stream.radioactive.fm port 8000: No route to host

mpd: Failed to decode http://radio.monash.edu:8002/hq; CURL failed: Failed to connect to radio.monash.edu port 8002: Connection refused

mpd: Failed to decode http://http-live.sr.se/srklassiskt-mp3-192; CURL failed: The requested URL returned error: 404 Not Available

mpd: Failed to decode http://icecast.vrtcdn.be/sporza-high.mp3; CURL failed: The requested URL returned error: 404 File Not Found

myURL.list contains 95 playable urls and 6 bad urls
```

### PLS files in a directory and its subdirectories
```
pi@moode:~ $ ./radiocheck.py .
./testpls/test1.pls missing 'File1=' and/or 'Title1=' line; skip to next pls file

. contains 5 pls files: 4 playable and 1 not playable
```

### PLS files in the moOde RADIO directory and its subdirectories
```
pi@moode:~ $ ./radiocheck.py RADIO
station: BBC Radio 2 - 320K
file: /var/lib/mpd/music/RADIO/BBC 320K Radio 2.pls
MPD Failed to decode http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_radio_two.m3u8

station: BBC Asian Network - 320K
file: /var/lib/mpd/music/RADIO/BBC 320K Asian Network.pls
MPD Failed to decode http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_asian_network.m3u8

/var/lib/mpd/music/RADIO/BBC Radio 5 live.pls missing 'File1=' and/or 'Title1=' line; skip to next pls file
...
station: Megarock Radio - All Request Rock Radio
file: /var/lib/mpd/music/RADIO/Megarock - All Request Rock Radio.pls
MPD Failed to decode http://stream1.megarockradio.net:8240/; CURL failed: The requested URL returned error: 404 File Not Found

/var/lib/mpd/music/RADIO contains 173 pls files: 163 playable and 10 not playable
```
