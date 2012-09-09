# Willhaben

Willhaben is a platform independent observer for the advertising platform [willhaben.at][]. If new ads match certain pre-defined criteria (e.g. keywords or price) Willhaben triggers a user notification. 

There are currently two ways you can run Willhaben:
* __Local__: It can run locally on MacOSX (>=10.8) or Linux/GTK (>=2.0) utilizing the platform's native notification environment.
* __Server__: If you run Willhaben on a server it will not use any GUI elements. Notifications are sent via email. Of course you can also run Willhaben locally in server mode. Since server mode does only depend on pure Python modules it should run on a variety of platforms.

## Dependencies

* Python (>=2.6)
* Python-beautifulsoup4
* PyObjC (OSX only)
* Python-notify2 (GTK only)

If you run Willhaben on a server you will only need the upper two.

## Setup

The setup process is straight forward. Copy the config file `files/willhaben.cfg.sample` to `files/willhaben.cfg` and edit it. The sample configuration is well commented and should be easy to grasp. That's it!

To launch Willhaben simply run `main.py`:

    python main.py

Willhaben will automatically look for the configuration file `files/willhaben.cfg`. However, you can create arbitrary configuration files and pass them as an argument:

    python main.py path/to/configfile.cfg

This way you can create various config files, one for every kind of ads you want to observe.

## Known issues

* GTK notification is currently somewhat broken. __notify2__ uses __Python-dbus__ to schedule GTK user notifications. However, it sometimes causes Willhaben to crash.
* If an ad article is free or the article is already sold the price is not recognized correctly and causes the observer to ignore a set price limit.

## Outlook

#### Short term
* Atom/RSS feed notifications
* Multiple types of notifications simultaneously
* Drop Local/Server distincion and replace with granular settings

#### Long term
* Support for arbitrary ad-based websites

[willhaben.at]: http://www.willhaben.at/