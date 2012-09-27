update-webfaction-dns
=====================

**update-webfaction-dns.py** [options] username:password[@machine] domain[@ip-adress] [, domain ...] ... updates your DNS override records at Webfaction.

* connects to Webfaction using SSL [https://api.webfaction.com/]
* machine is case-sensitive, so Web100 is Web100 and not web100.
* ip-address is optional. If omitted your current external IP will be fetched.

Available options are:

  -v           Verbose. Prints almost everything that happens.

  -h | --help  Prints this help-text.
