# UpdateJunkie

UpdateJunkie is a simple, platform independent agent for polling article-based websites. It started out as an observer for the advertising-platform [willhaben.at]. But by adding *profiles* one can observe all kinds of article-based websites. The following list shows an overview of the profiles that are currently supported:

* Willhaben: willhaben.at is an advertising service in Austria
* Willhaben Immo: The real estate section of willhaben.at

At the moment the only available notification type is email. But it should be very easy to extend UpdateJunkie with other notification types.

## Features

* Poll article-based websites and send email notifications
* Specify arbitrary tags in articles (e.g. price, description, post-time, etc.)
* Specify notification trigger-criteria based on tags (e.g. description contains X, price lower than Y, etc.)
* Handle paging in websites
* Persistent store of already processed articles
* Configurable entirely through a RESTful JSON API and/or a JSON startup script
* Easily extendable for new websites by using Python-based profiles
 
## Dependencies

* Python (>=3.0)
* BeautifulSoup 4 (for most profiles)

## Setup

To launch UpdateJunkie simply run `main.py`:

    python3 main.py

UpdateJunkie will look for a command script at `config/updatejunkie.json`. However, you can create arbitrary command scripts and pass them as an argument:

    python3 main.py path/to/commandscript.json

This way you can create various command scripts and run multiple instances simultaneously, if desired. Use `files/willhaben.json.example` as a template.

You can also start UpdateJunkie without a command script and configure it using only the JSON API.

## The Command API

The whole configuration of UpdateJunkie is based on commands. Commands can be send to UpdateJunkie in two ways:

* Via a web API (JSON)
* Via a JSON command script

In general you can launch UpdateJunkie without a command script. After launch UpdateJunkie can be configured using the web-based JSON API. If nothing else was configured (by a command script using the `web_settings` command), UpdateJunkie's web server listens on `http://localhost:8118`. However, it is recommended to use a command script to properly bootstrap UpdateJunkie. The root element in command scripts can either be a dictionary containing a single command, or a list of commands (see `config/updatejunkie.json.example`).

The web API uses the same command infrastructure as command scripts. Therefore all commands are available both ways. The only exception is the `web_settings` command which reconfigures the web server. Since this command restarts the web service during the execution it is not available via the web API.

For a full list of commands see the [commands] page in the wiki

[willhaben.at]: http://www.willhaben.at/
[commands]: https://github.com/kolomanschaft/updatejunkie/wiki/Commands