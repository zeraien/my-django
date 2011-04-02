This package contains a number of useful add-ons for the Django (www.djangoproject.com) framework.

# Module descriptions

## http

Helper functions and decorators for django views.

* render - similar to django's rendering shortcut, but more robust and better. Uses the "RequestContext" for rendering.

Decorators:

* @render_to("TEMPLATE_NAME")  - return a dictionary of values to export into the specified template, uses above render function to render.
* @render_json - anything returned from this function is converted into JSON (has to be a JSON encodable data structure or variable)
* @redirect - redirects to a URL that is returned from the view
* @permanent_redirect - same as above, but is a permanent redirect

## textblocks

Allows for dynamic content on your Django site.

To add this to your site, do the following in your base template:
`
{% load textblocks %}
{% load_textblock_support %}
`

Place your textblocks:

`{% load textblocks %}`

`{% textblock "main" %}`

`{% named_textbock "unique_name" %}`

Textblocks are automatically limited to the URL on which they are created.
You can use * as a wildcard symbol.

**NOTE:** Requires mootools 1.2

## logging

A basic logging framework for logging to the database.

In the future, I hope to integrate this more with Python's logging framework

## db

Offers a Pooled MySQL database backend for Django using sqlalchemy
