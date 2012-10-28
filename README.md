# Willhaben

Willhaben is a platform independent observer for the advertising platform [willhaben.at][]. If new ads match certain pre-defined criteria (e.g. keywords or price) Willhaben instantly triggers a user notification. Willhaben offers different notification options depending on the platform:

* GTK notifications
* OSX notification center (>= 10.8)
* Email notifications

If you only switch on email notifications, Willhaben only depends on pure Python modules and should run on a variety of platforms.

## Dependencies

* Python (>=2.6)
* Python-beautifulsoup4
* PyObjC (OSX only)
* Python-notify2 (GTK only)

If you run Willhaben on a server you will only need the upper two which are pure Python.

## Setup

The setup process is straight forward. Copy the config file `files/willhaben.cfg.sample` to `files/willhaben.cfg` and edit it. The sample configuration is well commented and should be easy to grasp. That's it!

To launch Willhaben simply run `main.py`:

    python main.py

Willhaben will automatically look for the configuration file `files/willhaben.cfg`. However, you can create arbitrary configuration files and pass them as an argument:

    python main.py path/to/configfile.cfg

This way you can create various config files, one for each kind of ads you want to observe.

## Known issues

* GTK notification is currently somewhat broken. __notify2__ uses __Python-dbus__ to schedule GTK user notifications which is working fine in most cases. However, it sometimes causes Willhaben to crash.
* If an ad article is free or the article is already sold the price is not recognized correctly and causes the observer to ignore a set price limit.

## Outlook

#### Short term
* Atom/RSS feed notifications

#### Long term
* Support for arbitrary ad-based websites

[willhaben.at]: http://www.willhaben.at/