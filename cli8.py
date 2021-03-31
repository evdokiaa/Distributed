#!/usr/bin/env python
# importing the required modules 
import os 
import sys
import argparse 
import requests
from requests.exceptions import HTTPError
import json
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'   

def command_palette():
	parser = argparse.ArgumentParser(
		prog = 'toycli',
		description = '''Toycli is a command line interface (CLI) for ToyChord.
						 The command palette offers song insertions, deletes and queries as well as node joins and departures.
						 You can also inspect the network's current state (ToyChord Ring) using the \"--overlay\" command.''',
		epilog = '''Use the \"--help\" command for additional toycli usage info.''')

	parser.add_argument("-n", "--node", type = str, nargs = 2, metavar = ("ip", "port"), help = "Declare the node ID.") 
	parser.add_argument("-j", "--join", action = 'store_true', help = "Select a node to join the ToyChord Network.") 
	parser.add_argument("-w", "--who", action = 'store_true', help = "View info about the position and the data of the node.") 
	parser.add_argument("-i", "--insert", 	type = str, nargs = 2, metavar = ('song', 'node_id'), default = None, help = "Insert a song. Input format should be: <song_title> <node_id>") 
	parser.add_argument("-if", "--insertfile", type = argparse.FileType('r'), nargs = '?', metavar = "file", default = None, help = "Insert songs from a file.") 
	parser.add_argument("-del", "--delete", type = str, nargs = 2, metavar = ('song', 'node_id'), default = None, help = "Delete a song/list of songs") 
	parser.add_argument("-q", "--query", 	type = str, nargs = '+', metavar = "song", default = None, help = "Search for a song/list of songs.") 
	parser.add_argument("-qf", "--queryfile",	type = argparse.FileType('r'), nargs = '?', metavar = "file",default = None, help = "Query songs from a file.") 
	parser.add_argument("-dep", "--depart", action = 'store_true', help = "Gracefully depart from the network.") 
	parser.add_argument("-o", "--overlay",  type = str, nargs = 1, metavar = "compact_view", choices = ['compact', 'extended'], help = "Inspect the current state of the network (ToyChord Ring).") 
	parser.add_argument("-r", "--requests",	type = argparse.FileType('r'), nargs = '?', metavar = "file", default = None, help = "Simulate usage through file requests.") 

	return parser

def url_handler(base_url, args):
	url = str()
##------------------------------------------------------
	if(args.join):
		url += base_url + "i_wanna_join/"
		response = requests.post(url)
		if response:
		    print(bcolors.OKBLUE + 'The node with:\n' + bcolors.OKCYAN + 'IP:\t'+ args.node[0] + '\nPort:\t' + args.node[1] + bcolors.OKBLUE + '\nsuccessfully joined the ToyChord Ring.' + bcolors.ENDC)
		else:
		    print(bcolors.WARNING + 'The node with:\n' + bcolors.OKCYAN + 'IP:\t'+ args.node[0] + '\nPort:\t' + args.node[1] + bcolors.OKBLUE + '\nfailed to join. Something went wrong!' + bcolors.ENDC)
		    print(bcolors.FAIL + 'status:' + str(response.status_code))
##------------------------------------------------------
	if(args.who):
		url += base_url + "whoami/"
		response = requests.get(url)
		if response:
		    # print(bcolors.OKBLUE + 'The node with:\n' + bcolors.OKCYAN + 'IP:\t'+ args.node[0] + '\nPort:\t' + args.node[1] + bcolors.OKBLUE + '\nsuccessfully joined the ToyChord Ring.' + bcolors.ENDC)
			json_object = json.loads(response.text)
			formatted_response = json.dumps(json_object, indent = 2, sort_keys = True)
			print(bcolors.OKBLUE + formatted_response + bcolors.ENDC)			
		else:
		    print(bcolors.WARNING + 'The node with:\n' + bcolors.OKCYAN + 'IP:\t'+ args.node[0] + '\nPort:\t' + args.node[1] + bcolors.OKBLUE + '\nfailed to join. Something went wrong!' + bcolors.ENDC)
		    print(bcolors.FAIL + 'status:' + str(response.status_code))
##------------------------------------------------------		    
	elif(args.depart):

		url += base_url + "i_wanna_depart/"
		response = requests.post(url)
		if response:
		    print(bcolors.OKBLUE + 'The node with:\n' + bcolors.OKCYAN + 'IP:\t'+ args.node[0] + '\nPort:\t' + args.node[1] + bcolors.OKBLUE + '\nsuccessfully departed.' + bcolors.ENDC)
		else:
		    print(bcolors.WARNING + 'The node with:\n' + bcolors.OKCYAN + 'IP:\t'+ args.node[0] + '\nPort:\t' + args.node[1] + bcolors.OKBLUE + '\nfailed to depart. Something went wrong!' + bcolors.ENDC)
		    print(bcolors.FAIL + 'status:' + str(response.status_code))
##------------------------------------------------------
	elif(args.overlay is not None):
		url += base_url + "overlay/"
		response = requests.post(url)
		if response:
			print(bcolors.OKBLUE + 'Here is the current state of the ToyChord Ring:' + bcolors.ENDC)
			if(args.overlay[0] == 'extended'):
				print(bcolors.OKCYAN + '<extensive overview mode>' + bcolors.ENDC)
				print(bcolors.OKBLUE + bcolors.BOLD + 'Nodes in the ring: ' + str(response.json()["counter"]) + bcolors.ENDC)
				json_object = json.loads(response.text)
				formatted_response = json.dumps(json_object, indent = 10, sort_keys = True)
				print(bcolors.OKBLUE + formatted_response + bcolors.ENDC)
			else:
				print(bcolors.OKCYAN + '<compact overview mode>' + bcolors.ENDC)
				nodes_num = response.json()["counter"]
				print(bcolors.OKBLUE + bcolors.BOLD + 'Nodes in the ring: ' + bcolors.OKCYAN + str(nodes_num) + bcolors.ENDC)
				for i in range(1,nodes_num+1):
					current_node = "node_" + str(i)
					node_position = str(response.json()[current_node]["my_position"])
					node_ip = str(response.json()[current_node]["my_ip"])
					node_port = str(response.json()[current_node]["my_port"])
					print(bcolors.OKBLUE + 'Node ' + str(i) + ' >> IP: ' + node_ip + ' >> Port: '+ node_port + ' >> Ring Position: ' + bcolors.OKCYAN + node_position + bcolors.ENDC)

		else:
			print(bcolors.WARNING + 'Failed to print the network\'s overlay.\nSomething went wrong!' + bcolors.ENDC)
			print(bcolors.FAIL + 'status:' + str(response.status_code))		
##------------------------------------------------------
	elif(args.delete is not None):
		url += base_url + "item/key"
		data = {"key":args.delete[0], "value":args.delete[1]}
		response = requests.delete(url, json = data)
		if response:
		    print(bcolors.OKBLUE + 'The song "'+ args.delete[0] + '" was successfully deleted.' + bcolors.ENDC)
		else:
		    print(bcolors.WARNING + 'The song "'+ args.delete[0] + '" was not deleted.\nSomething went wrong!' + bcolors.ENDC)
		    print(bcolors.FAIL + 'status:' + str(response.status_code))
##------------------------------------------------------
	elif(args.query is not None):
		url += base_url + "item/" + args.query[0]	
		response = requests.get(url)			
		if response:
		    print(bcolors.OKBLUE + 'The song "'+ args.query[0] + '" was found.' + bcolors.ENDC)
		else:
		    print(bcolors.WARNING + 'The song "'+ args.query[0] + '" was not found.\nSomething went wrong!' + bcolors.ENDC)
		    print(bcolors.FAIL + 'status:' + str(response.status_code))
##------------------------------------------------------
	elif(args.insert is not None):
		url += base_url + "item/key"
		data = {"key": args.insert[0], "value": args.insert[1]}
		response = requests.post(url, json = data)
		if response:
				print(bcolors.OKBLUE + 'The song "'+ bcolors.OKCYAN + args.insert[0] + bcolors.OKBLUE +'" was successfully inserted.' + bcolors.ENDC)
		else:
		    print(bcolors.WARNING + 'The song "'+ args.insert[0] + '" was not inserted.\nSomething went wrong!' + bcolors.ENDC)
		    print(bcolors.FAIL + 'status:' + str(response.status_code))
##------------------------------------------------------
	elif(args.insertfile is not None):
		# if(args.file[1] == 'i'):
		for line in args.insertfile:
			line = line.rstrip()
			title, node_p = line.split(", ")
			url = base_url + "item/keys"
			data = {"key": title, "value": node_p}
			response = requests.post(url, json = data)
			#print(response.text)
			if response:
				print(bcolors.OKBLUE + 'The song "'+ bcolors.OKCYAN + title + bcolors.OKBLUE +'" was ' + bcolors.WARNING + 'inserted' + bcolors.OKBLUE + ' with value: ' + bcolors.OKCYAN + str(node_p) + bcolors.ENDC)
			else:
				print(bcolors.WARNING + 'The song "'+ title + '" was not inserted.\nSomething went wrong!' + bcolors.ENDC)
				print(bcolors.FAIL + 'status:' + str(response.status_code))
##------------------------------------------------------
	elif(args.queryfile is not None):
		for line in args.queryfile:
			line = line.rstrip()
			url = base_url + "item/" + line	
			response = requests.get(url)			
			if response:
				value = response.json()["data"]["value"]
				#value = data["value"]
				#print(value)				
				#print(response.text)
				#formatted_response = json.dumps(json_object, indent = 0, sort_keys = True)
				message = response.json()["message"]
				if(message == 'a song was found'):
					value = response.json()["data"]["value"]			
					print(bcolors.OKBLUE + 'The song "'+ bcolors.OKCYAN + line + bcolors.OKBLUE +'" was ' + bcolors.OKGREEN + 'found' + bcolors.OKBLUE + ' with value: ' + bcolors.OKCYAN + str(value) + bcolors.ENDC)
				else:
					print(bcolors.OKBLUE + 'The song "'+ bcolors.OKCYAN + line + bcolors.OKBLUE +'" was ' + bcolors.FAIL + 'not found')
			else:
				print(bcolors.WARNING + 'The song "'+ bcolors.OKCYAN + line + bcolors.OKBLUE +'" was not found.\nSomething went wrong!' + bcolors.ENDC)
				print(bcolors.FAIL + 'status:' + str(response.status_code))
##------------------------------------------------------
	elif(args.requests is not None):
		for line in args.requests:
			line = line.rstrip()
			line = line.split(", ")
			if(line[0]  == 'insert'):
				url = base_url + "item/keys"
				data = {"key": line[1], "value": line[2]}
				response = requests.post(url, json = data)
				if response:
					print(bcolors.OKBLUE + 'The song "'+ bcolors.OKCYAN + line[1] + bcolors.OKBLUE +'" was ' + bcolors.WARNING + 'inserted' + bcolors.OKBLUE + ' with value: ' + bcolors.OKCYAN + str(line[2]) + bcolors.ENDC)
				else:
					print(bcolors.WARNING + 'The song "'+ line[1] + '" was not inserted.\nSomething went wrong!' + bcolors.ENDC)
					print(bcolors.FAIL + 'status:' + str(response.status_code))
			else:
				url = base_url + "item/" + line[1]	
				response = requests.get(url)			
				if response:
					value = response.json()["data"]["value"]
					#data = str(response.json()["data"])
					print(bcolors.OKBLUE + 'The song "'+ bcolors.OKCYAN + line[1] + bcolors.OKBLUE +'" was ' + bcolors.OKGREEN + 'found' + bcolors.OKBLUE + ' with value: ' + bcolors.OKCYAN + str(value) + bcolors.ENDC)
				else:
					print(bcolors.WARNING + 'The song "'+ bcolors.OKCYAN + line[1] + bcolors.OKBLUE +'" was not found.\nSomething went wrong!' + bcolors.ENDC)
					print(bcolors.FAIL + 'status:' + str(response.status_code))

	return response.text
	#return response.text
	#return url

def sys_measure(timer, tput_measure):

	hours, rem = divmod(timer, 3600)
	minutes, seconds = divmod(rem, 60)
	elapsed = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)
	print(bcolors.OKBLUE + '\n\t\t\t\t\t\tresponse time:\t' + bcolors.OKGREEN + elapsed + bcolors.OKBLUE + '' + bcolors.ENDC)
	if(tput_measure):
		req_num = 500
		tput = str(round(req_num/timer, 2))
		print(bcolors.OKBLUE + '\t\t\t\t\t\t   throughput:\t' + bcolors.OKGREEN + tput + bcolors.OKBLUE + ' songs/sec' + bcolors.ENDC)	

def main():

	#gia clear ths othonhs
	print(chr(27) + "[2J")

	# gia egkatastash tou neofetch:
	# add-apt-repository ppa:dawidd0811/neofetch
	# apt-get update
	# apt-get install neofetch
	os.system("neofetch")
	
	parser = command_palette()
	args = parser.parse_args()

	ip = args.node[0]
	port = args.node[1]
	url = str()
	url += "http://" + ip + ":" + port + "/"
	#print(url)
	tput_measure = args.insertfile or args.queryfile or args.requests is not None

	timer = time.time()
	json_data = url_handler(url, args)
	#time.sleep(1.5)
	timer = time.time() - timer
	sys_measure(timer, tput_measure)
	# json_object = json.loads(json_data)
	# formatted_response = json.dumps(json_object, indent = 10, sort_keys=True)
	#print(json_data)
		
if __name__ == "__main__": 
	main() 