from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask import jsonify
import sys, getopt
import hashlib
import requests
from flask import redirect
import threading 


app = Flask(__name__)
api = Api(app)

# o arithmos twn thesewn pou tha xrhsimopoihsoume gia to chord
global_modulo = 1024
linear = 0

bootstrap_ip = "127.0.0.1"
#bootstrap_ip = "[2001:648:2ffe:501:cc00:10ff:fe9d:6a92]"
bootstrap_port = 4096

my_ip = "127.0.0.1"
my_port = 0

def my_ip_port():
    global my_ip, my_port
    return my_ip + ":" + str(my_port)

next_node_ip = "127.0.0.1"
next_node_port = 0

previous_node_ip = "127.0.0.1"
previous_node_port = 0

#ip_who_made_request = "127.0.0.1"
#node_who_made_request = 0

am_i_bootstrap = False 

WITH_DATA = 1
WITHOUT_DATA = 0

#items = {"taksidiara_psyxi":"trypes", "diakopes_sto_sarajevo": "magic_de_spell", "fotia_sto_limani": "ksylina spathia"}
items = {}
replica_items = {}


#--------------------------------
def entos_twn_thesewn_mou(thesh_dedomenou):
    first, last = positions_i_am_responsible_for()
    if (first <=last and thesh_dedomenou >= first and thesh_dedomenou <= last):
        return True
    elif (last < first and ( thesh_dedomenou >= first or thesh_dedomenou <= last)):
        return True
    else: 
        return False
#--------------------------------


def hash_and_modulo(key, modulo): #hashes the argument string and returns the modulo of the hash with 16
    str = key
    # encoding GeeksforGeeks using encode() 
    # then sending to SHA256() 
    result = hashlib.sha256(str.encode()) 
  
    # printing the equivalent hexadecimal value. 
    #print("The hexadecimal equivalent of SHA256 is : ") 
    #print(result.hexdigest()) 
    #print("the modulo is:")
    #print(int(result % 16))
    x =  int(result.hexdigest(),16)
    #print(x % modulo)
    return x % modulo

def dummy_hash_and_modulo(key, modulo):
    #print('to kleidi einai: ', key)
    return int(key) % modulo

#oi theseis gia tis opoies einai ypeythinos o topikos komvos ksekinane  apo thn topikh thesh mexri kai mia thesh prin ton
#epomeno komvo, me ayth th synarthsh mporw na tsekarw poies einai aytes oi theseis gia na elegxw an kapoio dato pou mou stelnoun
#anhkei edw h kapou allou
def positions_i_am_responsible_for():
    first_position = hash_and_modulo(my_ip + ":" +  str(my_port), global_modulo)
    last_position = hash_and_modulo(next_node_ip + ":" + str(next_node_port), global_modulo) - 1
    if (my_port == next_node_port):
        return 0, global_modulo - 1
    elif ((last_position + 1) % global_modulo == 0):
        return int(my_port) % global_modulo, (global_modulo - 1)
    
    else:
        return first_position, last_position 

def dummy_positions_i_am_responsible_for():
    return 0, 15 

def dummy2_positions_i_am_responsible_for():
    if (my_port == next_node_port):
        return 0, 15
    elif (int(next_node_port) % 16 == 0):
        return int(my_port) % 16, 15
    else:
        return int(my_port) % 16, int(next_node_port) % 16 - 1

def pass_to_next(data):
    print("passing control to next")

def whoami(thelw_kai_ta_data):
    data = []
    rep_data = []
    #------------------------
    #first, last = dummy2_positions_i_am_responsible_for()
    first, last = positions_i_am_responsible_for()
    #------------------------
    if thelw_kai_ta_data == 1:
        for i in items:
            data.append({'key': i, 'value': items[i]})
        for i in replica_items:
            rep_data.append({'key': i, 'value': replica_items[i]})
    #data = {'message': 'songs were found', 'data': song_list}
    info = {"my_ip":my_ip, "my_port": my_port, 
    "next_ip":next_node_ip, "next_port": next_node_port,
    "previous_ip":previous_node_ip, "previous_port": previous_node_port,
    "am_i_bootstrap": am_i_bootstrap, "data": data, "rep_data":rep_data,
    #------------------------
    #'my_position': dummy_hash_and_modulo(my_port, 16),
    'my_position': hash_and_modulo(my_ip_port(), global_modulo),
    #------------------------
    'first_position': first,
    'last_position': last }
    return info

def initialize_info():
    global next_node_ip 
    global next_node_port 

    global previous_node_ip 
    global previous_node_port 

    global am_i_bootstrap 

    next_node_ip = "127.0.0.1"
    next_node_port = 0

    previous_node_ip = "127.0.0.1"
    previous_node_port = 0

    am_i_bootstrap = False

    global items
    items = {} 
            

# oi epomenes klaseis (Resources) ousiastika dhmiourgoun ta endpoints/urls mesw twn opoiwn tha ginetai h antallagh 
# mhnymatwn metaksy twn clients kai twn komvwn kai twn  
class Item(Resource):
    # H synarthsh ayth dexetai me get request ena key pou einai to onoma tou tragoudiou
    # eksetazei kat arxas an ayto to tragoudi prepei na periexetai ston topiko komvo
    # an nai eksetazei an ontws yparxei to tragoudi sth lista me ta items pou krataw topika
    # an to kleidi einai to asteraki tote epistrefei olh th lista...alla poia lista ayth pou exei topika? h kai olwn twn allwn
    # an eimai o prwtos komvos pou elava to request, tote sta dedomena pou stelnw stous epomenous, prepei me 
    # kapoio tropo na perasw kai thn ip -port mou gia na ta steilei se mena o armodios komvos apeytheias
    def get(self, key):
        items_position = hash_and_modulo(key, global_modulo)
        #------------------------
        #first, last = dummy2_positions_i_am_responsible_for()
        #first, last = positions_i_am_responsible_for()
        #------------------------

        if key == '**':
            song_list = []
            for i in items:
                song_list.append({'key': i, 'value': items[i]})
            response = {'message': 'songs were found', 'data': song_list}
            return jsonify(response)
        elif key == '*':
            url_of_mine = 'http://'+ my_ip + ':' + my_port + '/tapantaola/'
            return requests.post(url_of_mine).json()


        #if (key not in item.keys() and key not in replica_items.keys()):
        if (linear == 1):
            #------------------------
            #if((items_position < first or items_position > last ) and key not in replica_items.keys()):
            if( entos_twn_thesewn_mou(items_position) == False  and key not in replica_items.keys()):
            #------------------------
                url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/item/' + key
                return requests.get(url_of_next).json()
            if (key in items):
                if (number_of_replicas > 1 ):
                    to_next = {
                        'steps': number_of_replicas - 1,
                        'key': key
                    }
                    url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/linear_item/'
                    return( requests.post(url_of_next, json = to_next).json() )
                elif(number_of_replicas == 1):
                    response = {'message' : 'a song was found', 'data' : {'key': key, 'value': items[key]}}
                    return jsonify(response)
            elif (key in replica_items.keys()):
                to_next = {
                    'key': key,
                    'steps': number_of_replicas-1,
                    'is_replica':1
                }
                url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/linear_item/'
                return (requests.post(url_of_next, json = to_next).json())
            #------------------------    
            #elif (items_position >= first and items_position <= last):
            elif(entos_twn_thesewn_mou(items_position) == True):
            #------------------------    
                response = {'message': 'no song found'}
                return jsonify(response) 


        elif (linear == 0):
            #------------------------
            #if((items_position < first or items_position > last ) and key not in replica_items.keys()):
            if( entos_twn_thesewn_mou(items_position) == False and key not in replica_items.keys()):
            #------------------------
                url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/item/' + key
                return requests.get(url_of_next).json()  
            elif ( key in items.keys() ):   #or key in replica_items.keys() ):
                response = {'message' : 'a song was found', 'data' : {'key': key, 'value': items[key]}}
                return jsonify(response)       
            elif (key in replica_items.keys() ):
                response = {'message' : 'a song was found', 'data' : {'key': key, 'value': replica_items[key]}}
                return jsonify(response)
            #------------------------     
            #elif (items_position >= first and items_position <= last):
            elif(entos_twn_thesewn_mou(items_position) == True):
            #------------------------    
                response = {'message': 'no song found'}
                return jsonify(response) 

    # H synarthsh ayth lamvanei apo post request ta data pou einai
    # to key kai to value se mia morfh json 
    # px {key: "taksidiara psyxi", value: "trypes"}
    # dokimazei an to sygkekrimeno key anhkei se kapoia ap tis theseis gia tis opoies einai ypeythinos 
    # o topikos komvos mesw ths hash function
    # an oxi kalei to idio insert request gia ton epomeno komvo
    # an to sygkekrimeno key yparxei hdh kataxwrhmeno tote to kanoume overwrite opote h insert leitourgei san update
    def post(self, key):
        data = request.get_json(silent = True)

        items_position = hash_and_modulo(data["key"], global_modulo)
        #------------------------
        #first, last = dummy2_positions_i_am_responsible_for()
        #first, last = positions_i_am_responsible_for()
        #------------------------
        
        url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/item/' + key

        from_join = 0
        if ('del_last' in data.keys()):
            from_join = 1
        
        #------------------------
        #if( (items_position < first or items_position > last )and 'replica' not in data.keys()):
        if( entos_twn_thesewn_mou(items_position) == False and 'replica' not in data.keys()):
        #------------------------   
            return requests.post(url_of_next, json = data).json()
        #edw mpainei mono an to antikeimeno einai replica 
        #to del_last yparxei mono an einai apo join, opou tha prepei na diagrafei to teleytaio replica, 
        elif( 'replica' in data.keys() ):
            if (linear == 1 or from_join == 1):
                if ('del_last' not in data.keys()):
                    replica_items[data["key"]] = data["value"] 
                if (data['replica'] > 1):
                    data['replica'] -= 1 #epomeno replica 
                    return (requests.post(url_of_next, json = data).json())
                elif (data['replica'] == 1):
                    if ('del_last' in data.keys()):
                        del_next = {
                            'del_last':1,
                            "key": data["key"],
                            "value":data["value"],
                            "replica": 0
                        }
                        requests.post(url_of_next, json = del_next).json()
                    return (data['key'])
                elif (data['replica'] == 0):
                    replica_items.pop(data['key'])
                    return ('last_deleted')

            elif (linear == 0 and from_join == 0):
                replica_items[data["key"]] = data["value"] 
                if (data['replica'] > 1):
                    a = threading.Thread(target = eventual_item, args = ( data['key'], data['value'], data['replica'] - 1 ))
                    a.start()
                else:
                    return (data['key'])
            
        else:
            items[data["key"]] = data["value"]

            if (linear == 1 and number_of_replicas > 1 ) :    # (if k>1)
                to_next = {
                    "key":data["key"],
                    "value": data["value"],
                    "replica": number_of_replicas - 1
                }
                return requests.post(url_of_next, json = to_next).json()

            elif (linear == 0 and number_of_replicas > 1):
                a = threading.Thread(target = eventual_item, args = ( data['key'], data['value'], number_of_replicas-1) )
                a.start()
                return ( items )

            else: 
                return items

        #return items # Fetches first column that is Employee ID

    # Edw opws kai sthn insert lamvanoume mesw tou request ena kleidi eksetazoume an o topikos komvos einai ypeythinos
    # an oxi to prowthoume ston epomeno kanontas to antistoixo delete request pros ayton 
    # kai aytos otan to svhsei...logika tha prepei na mas steilei kapoio mhnyma epivevaiwshs...opote mallon tha prepei na 
    # pername kapws kai to ip mas pros tous epomenous opws kaname  kai sthn query 
    def delete(self, key):
        data = request.get_json(silent = True)

        items_position = hash_and_modulo(data["key"], global_modulo)
        
        #------------------------
        #first, last = dummy2_positions_i_am_responsible_for()
        #first, last = positions_i_am_responsible_for()
        #------------------------

        url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/item/' + key

        if (linear == 1):
            if ('replica' not in data.keys()):
                #------------------------
                #if(items_position < first or items_position > last ):
                if(entos_twn_thesewn_mou(items_position) == False):
                #------------------------
                    return requests.delete(url_of_next, json = data).json()
                elif (data["key"] in items.keys()):
                    items.pop(data["key"])
                    to_next = {
                        "key" : key,
                        "replica": number_of_replicas - 2
                    }
                    return requests.delete(url_of_next, json=to_next).json()
                else:
                    response = {
                        'message': 'no song to delete'
                    }
                    return jsonify( response )

            elif ('replica' in data.keys()):
                replica_items.pop(data["key"])
                if ( data["replica"] > 1) :
                    to_next = {
                        'replica': data["replica"],
                        'key':data['key']
                    }
                    return requests.delete(url_of_next, json=to_next).json() 
                else:
                    response = {
                        'message': 'song deleted',
                        'key': data['key']
                    }                              
                    return jsonify(response)

        elif (linear == 0 ):
            #------------------------
            #if((items_position < first or items_position > last) and 'replica' not in data.keys() ):
            if(entos_twn_thesewn_mou(items_position) == False and 'replica' not in data.keys() ):
            #------------------------    
                return requests.delete(url_of_next, json = data).json()
            elif ('replica' in data.keys()) :
                replica_items.pop(data["key"])
                if (data['replica'] > 1):
                    a = threading.Thread(target = delete_eventual_item, args = ( data['key'], data['replica'] - 1 ))
                    a.start()
                    response = {
                        'message': 'song deleted',
                        'key': data['key']
                    }
                    return jsonify(response)
                else:
                    response = {
                        'message': 'song deleted',                          
                        'key': data['key']
                    }                              
                    return jsonify(response)
            elif('replica' not in data.keys() ):
                if (data["key"] in items.keys()):
                    items.pop(data["key"])
                else :
                    response = {
                        'message': 'no song to delete'
                    }
                    return jsonify( response )
                if (number_of_replicas > 1):
                    a = threading.Thread(target = delete_eventual_item, args = ( data['key'], number_of_replicas - 1 ))
                    a.start()
                    response = {
                        'message': 'song deleted',
                        'key': data['key']
                    }
                    return jsonify(response)   
                else:
                    response = {
                        'message': 'song deleted',
                        'key': data['key']
                    }
                    return jsonify(response)                  

def delete_eventual_item (key, replica):
    to_next = {
        "key": key,
        "replica": replica
    }
    url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/item/' + key
    return requests.delete(url_of_next, json = to_next).json()

def eventual_item (key, value , replica):
    to_next = {
        "key": key,
        "value": value,
        "replica": replica
    }
    url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/item/' + key
    return requests.post(url_of_next, json = to_next).json()
    
class linear_item(Resource):
    def post(self):
        data = request.get_json(silent = True)

        if ('is_replica' not in data):
            if (data['steps'] > 1 ):   
                to_next = {
                    'steps': data['steps'] -1,
                    'key' : data['key']
                }
                url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/linear_item/'
                return requests.post(url_of_next, json = to_next).json()
            elif (data['steps'] == 1):
                if (data['key'] in replica_items.keys()):
                    response = {'message' : 'a song was found', 'data' : {'key': data['key'], 'value': replica_items[data['key']]}}
                    return jsonify(response)
                else:
                    response = {'message' : 'the song should be here'}
                    return jsonify(response)

        elif ('is_replica' in data):
            if ('last' in data ):
                response = {'message' : 'a song was found', 'data' : {'key': data['key'], 'value': replica_items[data['key']]}}
                return jsonify(response)
            elif (data['key'] in replica_items.keys()):
                to_next = {
                    'key' : data['key'],
                    'is_replica':1,
                    'steps': data['steps'] - 1,
                }
                url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/linear_item/'
                return requests.post(url_of_next, json = to_next).json()
            elif ( data['key'] not in replica_items.keys() ): 
                to_previous = {
                    'key' : data['key'],
                    'is_replica':1,
                    'last' : 1
                }
                url_of_previous = 'http://'+ previous_node_ip + ':' + str(previous_node_port) + '/linear_item/'
                return requests.post(url_of_previous, json = to_previous).json()

class Who_am_I(Resource):
    # ena url gia na pairnoume ta stoixeia tou kathe komvou
    def get(self):
       return(jsonify(whoami(WITH_DATA)))

class replica_in_node(Resource):
    def get(self, key):
        if(key in replica_items.keys()):
            response = {'message' : 'found'} 
            return (jsonify(response))
        else:
            response = {'message' : 'not_found'} 
            return (jsonify(response))

class update_after_join(Resource):
    def post(self):
        data = request.get_json(silent = True)
        if (data['max_steps']==0):
            return ('telos')
        rep_info = []
        for i in data['replicas']:
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/rep/' + i['key']
            a = requests.get(url_of_next).json()
            if(a['message'] == 'not_found'):
                replica_items.pop(i["key"])
            elif (a['message'] == 'found'):
                rep_info.append({'key': i['key'], 'value': i['value']})
        if (len(rep_info) > 0):
            to_next = {
                "replicas": rep_info,
                "max_steps": data['max_steps'] - 1
            }
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/update_after_join/'
            return requests.post(url_of_next, json = to_next).json()
        else :
            response = {
                'message' : 'join completed'
            }
            return jsonify(response)

class I_wanna_join(Resource):
    # me th synarthsh ayth o komvos pou thelei na mpei sto daktylio stelnei sxetiko request requests sto url 'join' tou bootstrap
    # tou stelnei mazi kai ta stoixeia tou to ip kai to port gia na ton katataksei o bootstrap sthn katallhlh thesh
    
    def post(self):
        url_of_bootstrap = 'http://'+ bootstrap_ip + ':' + str(bootstrap_port) + '/join/'
        info = {"my_ip":my_ip, "my_port": my_port}
        response = requests.post(url_of_bootstrap, json = info )
        
        global next_node_ip
        global next_node_port
        global previous_node_ip
        global previous_node_port

        next_node_ip = response.json()['next_ip']
        next_node_port = response.json()['next_port']
        previous_node_ip = response.json()['previous_ip']
        previous_node_port = response.json()['previous_port']

        #------------------------
        #first, last = dummy2_positions_i_am_responsible_for()
        #first, last = positions_i_am_responsible_for()
        #------------------------
        
        for i in response.json()['data']:
            hashed = hash_and_modulo(i['key'], global_modulo)
            #------------------------
            #if (hashed >= first and hashed <= last):
            if (entos_twn_thesewn_mou(hashed)):
            #------------------------
                items[i['key']] = i['value']
            elif (number_of_replicas > 1):                #an den einai diko tou alla tou prohgoumenou, tote prepei na parei ena replica
                replica_items[i['key']] = i['value']      # kai na diagrafei to teleytaio replica pou yparxei (gia na parameinei swstos
                url_of_next = 'http://'+ next_node_ip + ':' + next_node_port + '/item/' + 'a'          # o arithmos twn replicas
                to_next = {
                    "key" : i['key'],
                    "value" : i['value'], 
                    "replica": number_of_replicas - 2,
                    "del_last" : 1
                }
                requests.post(url_of_next , json=to_next)
        
        rep_info = []
        for i in response.json()['rep_data']:
            url_of_next = 'http://'+ next_node_ip + ':' + next_node_port + '/rep/' + i['key']
            a = requests.get(url_of_next).json()
            if(a['message'] == 'found'):
                rep_info.append({'key': i['key'] , 'value': i['value'] })
                replica_items[i['key']] = i['value']
        
        if(len(rep_info) > 0 ):
            url_of_next = 'http://'+ next_node_ip + ':' + next_node_port + '/update_after_join/'
            to_next = {
                "replicas": rep_info,
                "max_steps": number_of_replicas - 1
            }
            a = requests.post(url_of_next , json=to_next)
            print(a)
            
        return(response.json())

    #otan o komvos meta ton opoio tha topotheththei aytos pou thelei na kanei join, lavei to join aithma tha apanthsei se ayto edw
    #to url stelnontas ston komvo tous deiktes tou epomenou kai tou prohgoumenou komvou kathws kai to payload me ta items
    #pou prepei na prosthesei sthn topikh domh
    def put(self):
        pass

class Join(Resource):
    #  to aithma to dexetai arxika o bootstrap, kai an o komvos pou thelei na syndethei einai o amesws epomenos tou tote aytos taktopoiei th deiktodothsh
    #  kai th dianomh twn dedomenwn. Eidallws proothei to aithma me ta stoixeia tou epidoksou komvou ston epomeno tou daktyliou o opoios me th seira tou 
    # tha elegksei an o epidoksos prepei na mpei meta ap ayton kok
    def post(self):
        
        #------------------------
        #first, last = dummy2_positions_i_am_responsible_for()
        first, last = positions_i_am_responsible_for()
        #------------------------

        data = request.get_json(silent = True)
        #------------------------
        #aspiring_nodes_position = dummy_hash_and_modulo(data['my_port'], 16)
        new_node_ip_port = data['my_ip'] + ":" + data['my_port']
        aspiring_nodes_position = hash_and_modulo(new_node_ip_port, 16)
        #------------------------
        #print('thesh neou komvou: ',aspiring_nodes_position)

        # arxika pairnw tis theseis gia tis opoies o topikos komvos einai ypeythinos
        # kai elegxw an o neoeiserxomenos komvos katalamvanei mia apo aytes tis theseis
        #------------------------
        if ((aspiring_nodes_position > first and aspiring_nodes_position <= last) or (last < first and ( aspiring_nodes_position > first or aspiring_nodes_position <= last))): 
        #------------------------
            
            # se ayth thn periptwsh prepei na ginoun oi ekshs energeies
            # 1) ston komvo pou einai meta apo emena na pw (stelnontas ena request) na thesei ws prohgoumeno komvo ton kainourio
            # afou o kainourios tha mpei sto endiameso
            # 2) na allaksw egw pou lamvanw to aithma ton epomeno komvo mou kai na valw ton kainourio
            # 3) na steilw apanthsh ston kainourio komvo ta stoixeia pou tha prepei na valei ta opoia einai:
            #       ws prohgoumeno komvo prepei na thesei emena
            #       kai ws epomeno ayton pou eixa egw ws epomeno mexri twra
            #       epishs prepei na tou steilw kai ta dedomena pou tha exei gia na ta kataxwrhsei
            # genika kanoume oti kanoume se kyklika syndedemenes listes sthn C px  pou enhmerwnoume tous pointers
            global next_node_ip
            global next_node_port
            
            send_to_next = {"previous_ip": data['my_ip'] , "previous_port": data['my_port']}
            url_of_next = 'http://'+ next_node_ip + ':' + next_node_port + '/change_previous/'
            response_from_next = requests.post(url_of_next, json = send_to_next)

            info = []
            rep_info = []
            for i in items:
                info.append({'key': i, 'value': items[i]})
            for i in replica_items: 
                rep_info.append({'key': i, 'value': replica_items[i]})
            
            message_from_next = response_from_next.json()['message']
            if (message_from_next == 'success'):
                send_to_aspiring = {"previous_ip":my_ip, "previous_port": my_port, 
                "next_ip":next_node_ip, "next_port": next_node_port, 'data': info , 'rep_data':rep_info}
                
                next_node_ip = data['my_ip']
                next_node_port = data['my_port']
               
                #------------------------
                #first, last = dummy2_positions_i_am_responsible_for()
                first, last = positions_i_am_responsible_for()
                #------------------------
                items_copy = items.copy()
                for i in items_copy:
                    #------------------------
                    #???????????????????? edw thelei dieykrinhsh. Giati mono > last ?????
                    #if (hash_and_modulo(i, 16) > last):
                    if ( ((first <= last) and hash_and_modulo(i, global_modulo) > last) or (first > last and hash_and_modulo(i, global_modulo) > last  and  hash_and_modulo(i, global_modulo) < first)):
                    #------------------------        
                       items.pop(i)

                return jsonify(send_to_aspiring)
        #------------------------
        # sthn periptosh pou to hash kapoiou komvou taytizetai me kapoiou allou pou vrisketai hdh ston daktylio
        # tote to aithma eisagoghs aporriptetai
        elif (aspiring_nodes_position == first): 
            send_to_aspiring = {"status":"fail", "message": "h thesh tou komvou taytizetai me kapoion allo ston daktylio"}
        #------------------------

        else:
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/join/'
            return requests.post(url_of_next, json=data).json()

class Change_your_previous_node(Resource):
    def post(self):
        data = request.get_json(silent = True)
        global previous_node_ip 
        previous_node_ip = data['previous_ip']
        global previous_node_port 
        previous_node_port = data['previous_port']
        response = {'message':'success'}    

        return jsonify(response)

class I_wanna_depart(Resource):
    # me th synarthsh ayth o komvos pou thelei na fygei stelnei dyo requests sto url 'depart' tou prohgoumenou
    # kai tou epomenou komvou. An aytoi tou apanthsoun oti ola eginan ok..shmainei oti o komvos exei apodesmeythei epityxws
    # apo to daktylio
    def post(self):
        url_of_previous = 'http://'+ previous_node_ip + ':' + str(previous_node_port) + '/depart/'
        url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/depart/'

        info = whoami(WITH_DATA)
        
        response1 = requests.post(url_of_previous, json = info)
        response2 = requests.post(url_of_next, json = info)

        message1 = response1.json()['message']
        message2 = response2.json()['message']
        

        if message1 == 'success' and message2 == 'success':
            response = {'message' : 'efyga ola ok'} 
            initialize_info()
        
        else:
            response = {'message' : 'kati phge strava', 'message1': message1, 'message2': message2} 
          
        return jsonify(response)

class update_after_depart(Resource):
    def post(self):
        data = request.get_json(silent = True)
        
        replicas_to_next = []
        for i in data['replicas']:
            if i['key'] in replica_items.keys():
                replicas_to_next.append({'key': i['key'] , 'value': i['value'] })
            else:
                replica_items[i["key"]] = i["value"]

        if (len(replicas_to_next) > 0 ):
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/update_after_depart/'
            to_next = {
                'replicas': replicas_to_next,
                'max_steps': data['max_steps'] - 1
            }
            return requests.post(url_of_next , json=to_next).json()
        elif (len(replicas_to_next) == 0 or data['max_steps'] == 0):
            response = {
                'message': 'komple'
            }
            return jsonify(response)
        

class Depart(Resource):
    # Ayto to request to lamvanoun o prohgoumenos kai o epomenos komvos aytou pou feygei , o men prohgoumenos
    # thetei ws epomeno komvo tou ton epomeno aytou pou feygei, kai apothikeyei ola tou ta data
    # o de epomenos thetei ws prohgoumeno komvo tou ton prohgoumeno aytounou pou feygei
    
    def post(self):
        data = request.get_json(silent = True)
        global next_node_ip
        global next_node_port
        global previous_node_ip
        global previous_node_port

        if data['my_ip'] == next_node_ip and  data['my_port'] == next_node_port:
            next_node_ip = data['next_ip']
            next_node_port = data['next_port']
            for dato in data['data']:
                items[dato["key"]] = dato["value"]
            response = {'message' : 'success'}
            return jsonify(response)
        elif data['my_ip'] == previous_node_ip and  data['my_port'] == previous_node_port:
            previous_node_ip = data['previous_ip']
            previous_node_port = data['previous_port']
            if (number_of_replicas > 1):
                replicas_to_next = []
                for i in data['rep_data']:
                    if i['key'] in replica_items.keys():
                        replicas_to_next.append({'key': i['key'], 'value': i['value'] })
                    else:
                        replica_items[i["key"]] = i["value"]
                url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/update_after_depart/'
                to_next = {
                    'replicas': replicas_to_next,
                    'max_steps':number_of_replicas-1
                }
                a = requests.post(url_of_next , json=to_next).json()
                if (a['message'] == 'komple'):
                    response = {'message' : 'success'}
                    return jsonify(response)
                else:
                    response = {'message': 'wrong_replica_update'}
                    return jsonify(response)
            else:   
                response = {'message' : 'success'}
                return jsonify(response)
        else:
            response = {'message' : 'this node should not ask me to depart. i am not connected to it'}
            return jsonify(response)
        
        
class Test_redirect(Resource):
    #dokimastikh synarthsh gia na doume pws douleyei to redirect
    def get(self):
        url_of_bootstrap = 'http://'+ bootstrap_ip + ':' + bootstrap_port + '/whoami/'
        return redirect(url_of_bootstrap)

class Overlay(Resource):
    def post(self):
        data = request.get_json(silent = True)
        if data is None:
            data = {}
        if 'initial_ip' not in data.keys(): 
            data['counter'] = 1
            data['initial_ip'] = my_ip
            data['initial_port'] = my_port
            data['node_'+str(data['counter'])] = whoami(WITHOUT_DATA)
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/overlay/'
            return requests.post(url_of_next, json = data).json()

        
        elif (my_ip == data['initial_ip'] and my_port == data['initial_port']):
            return jsonify(data)
        
        else:
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/overlay/'
            data['counter'] = data['counter'] + 1
            data['node_'+str(data['counter'])] = whoami(WITHOUT_DATA)
            return requests.post(url_of_next, json = data).json()

class Ta_panta_ola(Resource):
    def post(self):
        data = request.get_json(silent = True)
        if data is None:
            data = {}
        if 'initial_ip' not in data.keys(): 
            data['counter'] = 1
            data['initial_ip'] = my_ip
            data['initial_port'] = my_port
            data['node_'+str(data['counter'])] = whoami(WITH_DATA)
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/tapantaola/'
            return requests.post(url_of_next, json = data).json()

        
        elif (my_ip == data['initial_ip'] and my_port == data['initial_port']):
            return jsonify(data)
        
        else:
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/tapantaola/'
            data['counter'] = data['counter'] + 1
            data['node_'+str(data['counter'])] = whoami(WITH_DATA)
            return requests.post(url_of_next, json = data).json()

class Test_request(Resource):
    # ayth einai kathara gia dokimastikous logous
    def post(self):
        print(request.headers)
        print(request.get_json())
        if ('ttl' not in request.get_json().keys()):
            print('mphka_edw')
            data = request.get_json() 
            data['ttl'] = 2
            url_of_next = 'http://'+ next_node_ip + ':' + str(next_node_port) + '/testreq/'
            
            print(data)
            #return redirect(url_of_next, code = 307)
            return requests.post(url_of_next, json = data).json()
        else: 
            return request.get_json()

api.add_resource(Item, '/item/<string:key>') # Route_1
api.add_resource(Who_am_I, '/whoami/') # Route_2
api.add_resource(I_wanna_join, '/i_wanna_join/') # Route_3
api.add_resource(Join, '/join/') # Route_4
api.add_resource(Test_redirect, '/testredirect/') # Route_5
api.add_resource(Depart, '/depart/') # Route_6
api.add_resource(I_wanna_depart, '/i_wanna_depart/') # Route_7
api.add_resource(Change_your_previous_node, '/change_previous/')
api.add_resource(Overlay, '/overlay/')
api.add_resource(Test_request, '/testreq/')
api.add_resource(replica_in_node, '/rep/<string:key>')
api.add_resource(update_after_join, '/update_after_join/')
api.add_resource(update_after_depart, '/update_after_depart/')
api.add_resource(Ta_panta_ola, '/tapantaola/')
api.add_resource(linear_item, '/linear_item/')

if __name__ == '__main__': # run  with command:  python node.py port_num ip
    #hash_and_modulo("chord dht", 16)
    my_port = sys.argv[1]
    my_ip = sys.argv[2]
    number_of_replicas = int(sys.argv[3])
    if (int(my_port) == 4096):
        am_i_bootstrap = True
        next_node_ip = my_ip
        next_node_port = my_port
        previous_node_ip = my_ip
        previous_node_port = my_port

    #app.run(host='::', port = my_port, debug = True)
    app.run(port = my_port, debug = True)