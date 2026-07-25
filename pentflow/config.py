"""PentFlow Configuration"""
from pathlib import Path

VERSION = "2.0.0"
PROJECT_NAME = "PentFlow"

# Paths
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"
TOOLS_DIR = BASE_DIR / "tools"

# Create dirs
for d in [SESSIONS_DIR, REPORTS_DIR, TEMPLATES_DIR, TOOLS_DIR]:
    d.mkdir(exist_ok=True)

# Scan defaults
DEFAULT_TIMEOUT = 10
DEFAULT_CONCURRENCY = 50
MAX_PORTS = 1000

# Wordlists
COMMON_PATHS = [
    "/", "/admin", "/login", "/register", "/api", "/robots.txt",
    "/sitemap.xml", "/.env", "/.git/config", "/wp-admin",
    "/wp-login.php", "/administrator", "/backup", "/config",
    "/debug", "/test", "/staging", "/dev", "/graphql",
    "/swagger", "/api/v1", "/api/v2", "/health", "/status",
    "/actuator", "/console", "/phpmyadmin", "/.well-known/security.txt",
    "/.htaccess", "/web.config", "/crossdomain.xml", "/clientaccesspolicy.xml",
    "/cgi-bin/", "/server-status", "/server-info", "/.DS_Store",
    "/.svn/entries", "/.bzr/", "/.hg/", "/CVS/ROOT",
    "/config.php", "/wp-config.php", "/database.yml",
    "/.env.local", "/.env.production", "/.env.development",
    "/api/docs", "/api/swagger", "/api/internal",
    "/backup.zip", "/backup.tar.gz", "/db.sql",
    "/dump.sql", "/export.csv", "/users.json",
]

COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "smtp", "pop", "imap", "webmail",
    "admin", "portal", "dev", "staging", "test", "api",
    "cdn", "static", "assets", "img", "images", "media",
    "blog", "shop", "store", "app", "mobile", "m",
    "vpn", "remote", "git", "gitlab", "jenkins", "ci",
    "db", "database", "mysql", "postgres", "mongo", "redis",
    "ns1", "ns2", "dns", "mx", "mx1", "mx2",
    "support", "help", "docs", "wiki", "kb",
    "monitor", "grafana", "kibana", "elastic",
    "grafana", "prometheus", "nagios", "zabbix",
]

TECH_SIGNATURES = {
    "WordPress": ["wp-content", "wp-includes", "wp-json"],
    "Joomla": ["joomla", "com_content"],
    "Drupal": ["drupal", "sites/default"],
    "Laravel": ["laravel", "XSRF-TOKEN"],
    "Django": ["csrfmiddlewaretoken", "django"],
    "Flask": ["werkzeug", "flask"],
    "React": ["react", "_next", "__NEXT_DATA__"],
    "Vue.js": ["vue", "vuejs"],
    "Angular": ["angular", "ng-version"],
    "Nginx": ["nginx"],
    "Apache": ["apache"],
    "IIS": ["Microsoft-IIS"],
    "Cloudflare": ["cloudflare", "cf-ray"],
    "PHP": [".php", "PHPSESSID"],
    "ASP.NET": ["aspx", "asp.net"],
    "Ruby on Rails": ["_rails", "ruby"],
    "Java": ["java", "JSESSIONID"],
    "Node.js": ["express", "x-powered-by: Express"],
}

# GitHub integration
GITHUB_ENABLED = True
GITHUB_AUTO_PUSH = False  # Set True to auto-push reports
