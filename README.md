Webfaction CLI
==============

**webfaction.py** //[options] username:password[@machine] action arguments [, action ...] ...// calls the Webfaction API with specified actions and arguments.

* connects to Webfaction using SSL [https://api.webfaction.com/]
* machine is case-sensitive, so Web100 is Web100 and not web100.

Available actions are:
----------------------

### **create_dns_override** //domain[@ip-address]//

* Creates a DNS override. The domain must be created first.
* ip-address is optional. If omitted your current external IP will be fetched.

### **delete_dns_override** //domain[@ip-address]//

* Deletes a DNS override.

### **list_dns_overrides**
* Prints a list with all dns overrides.
* Pattern: { 'key': 'value' }

Available options are:
----------------------

* **-v** Verbose. Prints almost everything that happens.
* **-h** | **--help**  Prints this help-text.
