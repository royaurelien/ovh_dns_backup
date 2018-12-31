# -*- encoding: utf-8 -*-

import argparse
from datetime import datetime
import json
import os
import sys
import ovh

"""
	OVH DNS backup tool
	-------------------
"""
__all__ = ['backup']

_name = 'OVH DNS backup tool'
_desc = 'Backup DNS zone'
_epilog = """
ovh.conf example
----------------------
[default]
endpoint=ovh-eu

[ovh-eu]
application_key=xxx
application_secret=xxx
consumer_key=xxx
----------------------
"""

EXPORT_PATH = '/tmp'
OVH_VARS = ['endpoint', 'application_key', 'application_secret', 'consumer_key']
OVH_CONF = 'ovh.conf'

def __gen_name():
	return datetime.now().strftime('%Y-%m-%d')

def _export_zone(api):
	for zoneName in api.get('/domain/zone'):
		zone = api.get('/domain/zone/{}/export'.format(zoneName))
		yield (zoneName, zone)
		
def _get_parser():
    """
    :return: argparse object
    """
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser(prog=_name, 
    	description=_desc, 
    	epilog=_epilog, 
    	formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-d", "--destination", required=False, help="backup folder", default=EXPORT_PATH)
    ap.add_argument("-e", "--endpoint", required=False, help="endpoint")
    ap.add_argument("-k", "--application_key", required=False, help="application key")
    ap.add_argument("-s", "--application_secret", required=False, help="application secret")
    ap.add_argument("-c", "--consumer_key", required=False, help="consumer key")

    return ap

def _check_args(args):
	return all([v for k,v in args.items() if k in OVH_VARS])

def _check_config_file():
	return os.path.exists(os.path.join(os.getcwd(), OVH_CONF))

def _get_api(**args):
	return ovh.Client(**dict((k,v) for k,v in args.items() if v and k in OVH_VARS))

def _create_backup_path(path=EXPORT_PATH):
	backup_path = os.path.join(path, __gen_name())
	
	# check / create backup directory
	if not os.path.exists(backup_path):
		try:
			os.makedirs(backup_path)
		except OSError as err:
			print("OS error: {0}".format(err))

	return backup_path

def __backup(api, dest):
	count = 0
	for name, zone in _export_zone(api):
		with open(os.path.join(dest, name), 'w') as f:
			f.write(zone)
		count += 1
	return count

def backup(**kwargs):
	
	if not _check_args(kwargs) and not _check_config_file():
		raise ValueError('Please provide correct configuration')

	api = _get_api(**kwargs)
	dest = _create_backup_path(kwargs.get('destination', EXPORT_PATH))
	count = __backup(api, dest)

	return count

def main():
	parser = _get_parser()
	args = vars(parser.parse_args())

	res = backup(**args)
	sys.exit(0)

# def main():
# 	parser = _getParser()
# 	args = vars(parser.parse_args())

# 	# check ovh configuration vars
# 	if not all([v for k,v in args.items() if k in OVH_VARS]):
# 		# check ovh.conf file in current directory
# 		if not os.path.exists(os.path.join(os.getcwd(), 'ovh.conf')):
# 			sys.exit('ovh configuration not found')

# 	api = ovh.Client(**dict((k,v) for k,v in args.items() if k in OVH_VARS))

# 	folder = _getFolder()
# 	path = os.path.join(args.get('destination'), folder)

# 	# check / create backup directory
# 	if not os.path.exists(path):
# 		try:
# 			os.makedirs(path)
# 		except OSError as err:
# 			print("OS error: {0}".format(err))
# 			sys.exit(1)

# 	# export dns zone
# 	for name, zone in _exportZone(api):
# 		with open(os.path.join(path, name), 'w') as f:
# 			f.write(zone)

# 	sys.exit(0)

if __name__ == '__main__':
	main()

