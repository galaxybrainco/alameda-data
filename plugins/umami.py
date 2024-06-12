from datasette import hookimpl


@hookimpl
def extra_body_script():
    return {
        "script": '</script><script defer src="https://analytics.civic.band/sunshine" data-website-id="43ac0bfd-5789-4d27-9c9b-409d11e092d1">'
    }
