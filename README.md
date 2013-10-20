# Willhaben

Willhaben is a platform independent web crawler for article-based websites. It started out as an observer for the advertising-platform [willhaben.at]. But by adding *profiles* one can observe all kinds of article-based websites. The following list shows an overview of the profiles that are currently supported:

* Willhaben: willhaben.at is an advertising service in Austria
* DoodleComments: Observes the comments section of Doodle schedule pages

At the moment the only available notification type is email. But it should be very easy to extend Willhaben with other notification types.

## Dependencies

* Python (>=2.6)
* Python-beautifulsoup4

## Setup

The setup process is straight forward. Copy the config file `files/willhaben.cfg.sample` to `files/willhaben.cfg` and edit it. The sample configuration is well commented and should be easy to grasp. That's it!

To launch Willhaben simply run `main.py`:

    python main.py

Willhaben will automatically look for the configuration file `files/willhaben.cfg`. However, you can create arbitrary configuration files and pass them as an argument:

    python main.py path/to/configfile.cfg

This way you can create various config files, one for each kind of ads you want to observe.

## Profiles

Profiles are stored in the `connector_profiles` folder. Each XML file in this folder represents a particular website (or a certain part of it) and contains information about how to access the website and how to find articles on its pages. If you want to adapt Willhaben for a new website, all you should have to do is create a new profile.

### Profile Creation

To make the process of creating a new profile as easy as possible, Willhaben comes with a XML Schema file located at `connector_profiles/profile.xsd`. If you are using an advanced XML editor (like the one in the Eclipse Web Tools Platform) you can validate your profile while you write it.

The original Willhaben profile (`connector_profiles/willhaben.xml`) is very well documented. This should be enough to get you started with new profiles. You can use the script `profile_tester.py` to help you during the profile creation. It takes a profilename and a URL as arguments and tests the profile against the given URL.

## Known issues

* If an ad article is free or the article is already sold the price is not recognized correctly and causes the observer to ignore a set price limit.

## Outlook

I'm planning to make Willhaben a server/client application with the present application being the server. Therefore the configurtaion will no longer be fetched from a cfg-file. Instead Willhaben will be accessable over a simple JSON API.

[willhaben.at]: http://www.willhaben.at/
