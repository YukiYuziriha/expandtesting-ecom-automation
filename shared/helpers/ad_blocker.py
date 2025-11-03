import re
from playwright.sync_api import Route, BrowserContext

AD_DOMAINS = [
    # Google Ad Services (the main culprits)
    "googleads.g.doubleclick.net",
    "pagead2.googlesyndication.com",
    "ad.doubleclick.net",
    "googleadservices.com",
    "googlesyndication.com",
    "doubleclick.net",
    "ads.google.com",
    "adservice.google.com",
    # Analytics/Tracking
    "google-analytics.com",
    "analytics.google.com",
    # Other common ad networks
    "taboola.com",
    "outbrain.com",
    "adnxs.com",
    "ads.yahoo.com",
    "ads.bing.com",
    "adserver.org",
    "adtech.com",
    "advertising.com",
    "atdmt.com",
    "exponential.com",
    "fastclick.net",
    "media.net",
    "openx.net",
    "pubmatic.com",
    "rubiconproject.com",
    "smartadserver.com",
    "yieldmanager.com",
    "google_vignette",
    "enshrouded.com",
]


def handle_route(route: Route) -> None:
    """Intercept and block requests to ad domains."""
    if any(re.search(domain, route.request.url) for domain in AD_DOMAINS):
        route.abort()
    else:
        route.continue_()


def block_ads_on_context(context: BrowserContext) -> None:
    """Attach ad blocking route handler to a browser context."""
    context.route("**/*", handle_route)
