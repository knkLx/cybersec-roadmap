import aiohttp
from utils.config import USER_AGENT

TECH_SIGNATURES = {
    "WordPress": ["wp-content", "wp-includes", "wp-json"],
    "Joomla": ["joomla", "com_content", "/administrator/"],
    "Drupal": ["drupal", "sites/default/files"],
    "Laravel": ["laravel", "XSRF-TOKEN", "laravel_session"],
    "Django": ["csrfmiddlewaretoken", "django"],
    "Flask": ["werkzeug", "flask"],
    "React": ["react", "_next", "__NEXT_DATA__"],
    "Vue.js": ["vue", "vuejs", "__vue__"],
    "Angular": ["angular", "ng-version"],
    "Bootstrap": ["bootstrap.min.css", "bootstrap.min.js"],
    "jQuery": ["jquery", "jquery.min.js"],
    "Nginx": ["nginx"],
    "Apache": ["apache", "Apache/"],
    "IIS": ["Microsoft-IIS"],
    "Cloudflare": ["cloudflare", "cf-ray"],
    "AWS": ["amazonaws", "aws"],
    "Google Cloud": ["googleapis", "gcp"],
    "PHP": [".php", "PHPSESSID"],
    "ASP.NET": ["aspx", "asp.net", "__VIEWSTATE"],
    "Ruby on Rails": ["_rails", "ruby"],
    "Varnish": ["x-varnish", "varnish"],
    "OpenResty": ["openresty"],
    "LiteSpeed": ["litespeed"],
}


async def detect(target: str) -> list[str]:
    url = target if target.startswith("http") else f"https://{target}"
    found = set()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=15),
                allow_redirects=True,
                ssl=False,
            ) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                body = await resp.text()

                # Check headers
                server = headers.get("server", "")
                powered = headers.get("x-powered-by", "")
                combined = f"{server} {powered}".lower()
                for tech, sigs in TECH_SIGNATURES.items():
                    if any(s.lower() in combined for s in sigs):
                        found.add(tech)

                # Check body
                body_lower = body.lower()
                for tech, sigs in TECH_SIGNATURES.items():
                    if any(s.lower() in body_lower for s in sigs):
                        found.add(tech)

    except Exception as e:
        print(f"[!] Tech detection error: {e}")
    return sorted(found)
