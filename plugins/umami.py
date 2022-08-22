from datasette import hookimpl


@hookimpl
def extra_body_script():
    return {
        "script": '</script><script async defer data-website-id="284d1d59-65bc-4abb-9fd0-3a2f976d518e" src="https://analytics.alameda.one/civic.js">'
    }
