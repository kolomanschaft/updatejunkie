# UpdateJunkie

UpdateJunkie is a simple, platform independent crawler for article-based websites. It started out as an observer for the advertising-platform [willhaben.at]. But by adding *profiles* one can observe all kinds of article-based websites. The following list shows an overview of the profiles that are currently supported:

* Willhaben: willhaben.at is an advertising service in Austria
* Willhaben Immo: The real estate section of willhaben.at

At the moment the only available notification type is email. But it should be very easy to extend UpdateJunkie with other notification types.

## Features

* Observe article-based websites and send email notifications
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

The whole configuration of UpdateJunkie is based on commands. Commands are encoded as JSON and can be send to UpdateJunkie in two ways:

* Via a HTTP API
* Via a command script

You can launch UpdateJunkie without a command script. After launch UpdateJunkie can be configured using the web-based JSON API. If nothing else was configured (by a command script), UpdateJunkie's web server listens on `localhost` and port `8118`. However, it is recommended to use a command script to properly bootstrap UpdateJunkie. The root element in command scripts can either be a dictionary containing a single command, or a list of commands (see `config/updatejunkie.json.example`).

Use the JSON API by calling `http://host:port/api/command`. Each API call is terminated by a response which is also JSON. The response states whether the command was successful or not and contains a response data structure if necessary. In case the command failed, the response contains an error message.

Example for a successful command response:
```JSON
{
	"status": "OK",
	"response": ["mydata", 25, false]
}
```

Keep in mind that the `response` key/value-pair is optional.

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

#### create_observer

Adds a new observer and activates it. This is the most complex command as it contains the whole configuration for an observer. Therefore here is a brief explanation about what each element does. It might be worth mentioning that none of the root-level elements is optional.

__name__: The observer's name<br />
__profile__: The website's profile. More about profiles in the next section<br />
__url__: The URL of the page where the articles are located<br />
__store__: If `true`, UpdateJunkie remembers already processed ads upon restarts<br />
__interval__: Time between two polls<br />
__criteria__: A list of trigger criteria

You can specify a set of criteria which have to be satisfied in order to trigger notifications (logical AND). If at least one criterion doesn't match, no notification will be triggered. (Note: There might be efforts in the future to enable building complex logical expressions with triggers as atomic elements.)

__tag__: The name of the tag as defined in the website profile<br />
__type__: One out of `keywords_any`, `keywords_all`, `keywords_not`, `less_than`, `greater_than`<br />
__keywords__: A list of keywords (only available for types `keywords_*`)<br />
__limit__: A number value that is the upper or lower bound of an integer or float type tag (only available for criterion types `less_than` and `greater_than`)

Example:
```JSON
{
    "command": "create_observer",
    "name": "Reboarder",
    "profile": "Willhaben",
    "url": "http://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?CATEGORY/MAINCATEGORY=68&CATEGORY/SUBCATEGORY=3914&BABYPRAMS_DETAIL=1",
    "store": true,
    "interval": 120,
    "criteria":
    [
        {
            "tag": "description",
            "type": "keywords_any",
            "keywords": [ "reboarder", "re-board", "re-boarder" ]
        },
        {
            "tag": "price",
            "type": "less_than",
            "limit": 350
        }
    ]
}
```

Response: *None*

#### add_notification

Adds a notification to an existing observer. Whenever an ad matches the observer's criteria all attached notifications will be triggered.

__type__: The notification type. At this moment `email` is the only option.<br />
__observer__: The name of the observer to which the notification should be attached.<br />

The following keys are depending on the notification type.

##### Type `email`

__from__: What appears in the email's sender-header.<br />
__to__: The email recipients (this value is an array!).<br />
__mime_type__: The email MIME-type.<br />
__subject__: The email subject.<br />
__body__: The email body.<br />

Note: The email notification needs a properly configured SMTP server (command `smtp_config`). Otherwise the command will fail. 

Example:
```JSON
{
    "command": "add_notification",
    "type": "email",
    "observer": "Reboarder",
    "from": "UpdateJunkie <junkie@example.com>",
    "to": [ "John Doe <john@example.com>" ],
    "mime_type": "text/html",
    "subject": "{title} for {price}",
    "body": "I found a new ad ({datetime}):<br/><br/>\n<b>{title}</b><br/>\nfor € <b>{price}</b><br/><br/>\n<a href=\"{url}\">{url}</a><br/><br/>\nbye!"
}
```

Response: *None*

#### get_observer

Returns a data structure that contains the same elements as the `create_observer` command except for the `command` specifier itself. You could take the response directly to add the same observer.

Example:
```JSON
{
	"command": "get_observer",
	"name": "Reboarder"
}
```

Response:
```JSON
{
    "command": "create_observer",
    "name": "Reboarder",
    "profile": "Willhaben",
    "url": "http://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?CATEGORY/MAINCATEGORY=68&CATEGORY/SUBCATEGORY=3914&BABYPRAMS_DETAIL=1",
    "store": true,
    "interval": 120,
    "criteria":
    [
        {
            "tag": "description",
            "type": "keywords_any",
            "keywords": [ "reboarder", "re-board", "re-boarder" ]
        },
        {
            "tag": "price",
            "type": "less_than",
            "limit": 350
        }
    ]
}
```

#### smtp_config

Set the SMTP configuration used to send emails.

Example:
```JSON
{
	"command": "smtp_config",
	"host": "smtp.example.com",
	"port": 587,
	"user": "felix_the_cat",
	"pass": "fracking_password"
}
```

Response: *None*

## Profiles

Profiles are stored in the `profiles` Python package. A profile specifies how to parse a certain content-based website. The heart of a profile is the method `parse(html)`. It takes a string containing HTML code and returns an iterator yielding the parsed ads.

If you want to extend UpdateJunkie to parse new websites you just have to create a new profile. Your are welcome to send me a pull request for profiles you've created.

### Profile Creation

All profiles are derived from a base class `ProfileBase`. This is your starting point. Create a new module within the `profile` package that has the same name as your profile. Create a new class derived from `ProfileBase` and implement all required properties and methods.

#### Required Properties

__tags__: A dictionary containing all tags as its keys that define a single ad. The values should be default values that define the tag's type. A parsed ad should be represented by an identical dictionary (with different values).<br />
__key_tag__: The name of a tag that can be used as identifier. The key tag must be unique and time-invariant.<br />
__datetime_tag__: The name of a tag that contains a datetime. If the website does not provide time information for ads you could use the time the ad was parsed.<br />

#### Required methods

__parse(html)__: Takes a string containing HTML code of the website and returns an iterator. Every iteration should yield a parsed ad encoded as a dictionary. The dictionary should have the same keys as the `tags` property.<br />

#### Optional Properties

__paging_param__: The name of a HTTP parameter that can be used to indicate the page (e.g. http://example.com/?p=2).<br />
__paging_param_init__: The value of the paging parameter that belongs to the first page.<br />
__paging_method__: The HTTP method of the paging parameter (GET, POST).<br />
__encoding__: The content encoding of the website (in case the charset is not specified in the HTML head).<br />

## Known issues

* Profile `Willhaben`: If an ad article is free or the article is already sold the price is not recognized correctly and causes the observer to ignore a set price limit.

[willhaben.at]: http://www.willhaben.at/
