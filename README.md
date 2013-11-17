# UpdateJunkie

UpdateJunkie is a simple, platform independent crawler for article-based websites. It started out as an observer for the advertising-platform [willhaben.at]. But by adding *profiles* one can observe all kinds of article-based websites. The following list shows an overview of the profiles that are currently supported:

* Willhaben: willhaben.at is an advertising service in Austria
* DoodleComments: Observes the comments section of Doodle schedule pages

At the moment the only available notification type is email. But it should be very easy to extend UpdateJunkie with other notification types.

## Features

* Observe article-based websites and send email notifications
* Specify arbitrary tags in articles (e.g. price, description, post-time, etc.)
* Specify notification trigger-criteria based on tags (e.g. description contains X, price lower than Y, etc.)
* Handle paging in websites
* Persistent store of already processed articles
* Configurable entirely through a RESTful JSON API and/or a JSON startup script
* Easily extendable for new websites by using XML-based profiles
 
## Dependencies

* Python (>=3.0)

## Setup

To launch UpdateJunkie simply run `main.py`:

    python3 main.py

UpdateJunkie will look for a command script at `files/willhaben.json`. However, you can create arbitrary command scripts and pass them as an argument:

    python3 main.py path/to/commandscript.json

This way you can create various command scripts and run multiple instances simultaneously, if desired. Use `files/willhaben.json.example` as a template.

You can also start UpdateJunkie without a command script and configure it using only the JSON API.

## The Command API

The whole configuration of UpdateJunkie is based on commands (the only exceptions are profiles which are discussed in the next chapter). Commands are encoded in JSON and can be send to UpdateJunkie in two ways:

* Via a HTTP API
* Via a command script

You can launch UpdateJunkie without a command script. After launch UpdateJunkie can be configured using the web-based JSON API. If nothing else was configured (by a command script), UpdateJunkie's web server listens on `localhost` and port `8118`. However, it is recommended to use a command script to properly bootstrap UpdateJunkie. The root element in command scripts can either be a dictionary containing a single command, or a list of commands (see `files/willhaben.json.example`).

Use the JSON API by sending commands to `http://host:port/api/command`. Each API call is terminated by a response which is also JSON. The response states whether the command was successful or not and contains a response data structure if necessary. In case the command failed, the response contains an error message.

Example for a successful command response:
```JSON
{
	"status": "OK",
	"response": ["mydata", 25, false]
}
```

Example for a failed command response:
```JSON
{
	"status": "ERROR",
	"message": "JSON syntax: Expecting , delimiter: line 3 column 2 (char 33)"
}
```

Upcoming is a list of commands that the API currently supports.

### Available Commands

#### list_commands

Returns a list of all available commands.

Example:
```JSON
{
	"command": "list_commands"
}
```

Response:
```JSON
["<command1>", "<command2>", ...]
```

#### list_observers

Returns a list of all observers which are currently active.

Example:
```JSON
{
	"command": "list_observers"
}
```

Response:
```JSON
["MyObserver", "AnotherObserver", ...]
```

#### remove_observer

Removes an active observer.

Example:
```JSON
{
	"command": "remove_observer",
	"name": "<observer_name>"
}
```

Response: *None*

#### new_observer

Adds a new observer and activates it. This is the most complex command as it contains the whole configuration for an observer. Therefore here is a brief explanation about what each element does. It might be worth mentioning that none of the elements in the first level is optional.

__name__: The observer's name<br />
__profile__: The website's profile. More about profiles in the next section<br />
__url__: The URL of the page where the articles are located<br />
__store__: If `true`, UpdateJunkie remembers already processed ads upon restarts<br />
__interval__: Time between two polls<br />
__criteria__: A list of trigger criteria

You can specify a set of criteria which have to be satisfied in order to trigger a notification. If at least one criterion doesn't match, no notification will be triggered.

__tag__: The name of the tag as defined in the website profile<br />
__type__: One out of `keywords_any`, `keywords_all`, `keywords_not`, `limit`<br />
__keywords__: A list of keywords (only available for types `keywords_*`)<br />
__limit__: A number value that is the upper bound of an integer or float type tag (only available for criterion type `limit`)

You can specify notifications for that observer. At the moment the only available notification type is `email` but there might be more in the future.

__type__: One out of `email`, ... well thats it<br />
__to__: A list of email recipients

Example:
```JSON
{
	"command": "new_observer",
	"name": "Bugaboo",
	"profile": "Willhaben",
	"url": "http://www.willhaben.at/iad/kaufen-und-verkaufen/baby-kind/transport/",
	"store": true,
	"interval": 30,
	"criteria":
	[
		{
			"tag": "title",
			"type": "keywords_any",
			"keywords": [ "bugaboo" ]
		},
		{
			"tag": "title",
			"type": "keywords_not",
			"keywords": [ "teutonia" ]
		}
		{
			"tag": "price",
			"type": "limit",
			"limit": 50
		}
	],
	"notifications":
	[
		{
			"type": "email",
			"to": [ "Martin Hammerschmied <gestatten@gmail.com>" ]
		}
	]
}
```

Response: *None*

#### get_observer

Returns a data structure that contains the same elements as the `new_observer` command except for the `command` specifier itself. You could take the response directly to add another observer.

Example:
```JSON
{
	"command": "get_observer",
	"name": "Bugaboo"
}
```

Response:
```JSON
{
	"profile": "Willhaben",
	"name": "Bugaboo",
	"url": "http://www.willhaben.at/iad/kaufen-und-verkaufen/baby-kind/transport/",
	"interval": 30,
	"notifications":
	[
		{
			"to": ["Martin Hammerschmied <gestatten@gmail.com>"],
			"type": "email"
		}
	],
	"criteria":
	[
		{
			"keywords": ["bugaboo"],
			"tag": "title",
			"type": "keywords_any"
		},
		{
			"keywords": ["teutonia"],
			"tag": "title",
			"type": "keywords_not"
		},
		{
			"limit": 50,
			"tag": "price",
			"type": "limit"
        	}
	],
	"store": true
}
```

#### smtp_config

Set the SMTP configuration used to send emails.

Example:
```JSON
{
	"command": "smtp_config",
	"host": "smtp.example.com",
	"port": 25,
	"user": "felix_the_cat",
	"pass": "fuckingpassword"
}
```

Response: *None*

## Profiles

Profiles are stored in the `connector_profiles` folder. Each XML file in this folder represents a particular website (or a certain part of it) and contains information about how to access the website and how to find articles on its pages. If you want to adapt UpdateJunkie for a new website, all you should have to do is create a new profile.

### Profile Creation

To make the process of creating a new profile as easy as possible, UpdateJunkie comes with a XML Schema file located at `connector_profiles/profile.xsd`. If you are using an advanced XML editor (like the one in the Eclipse Web Tools Platform) you can validate your profile while you write it.

The original Willhaben profile (`connector_profiles/willhaben.xml`) is very well documented. This should be enough to get you started with new profiles. You can use the script `profile_tester.py` to help you during the profile creation. It takes a profilename and a URL as arguments and tests the profile against the given URL.

## Known issues

* Profile `Willhaben`: If an ad article is free or the article is already sold the price is not recognized correctly and causes the observer to ignore a set price limit.

[willhaben.at]: http://www.willhaben.at/
