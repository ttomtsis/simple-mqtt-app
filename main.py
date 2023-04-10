# ΔΙΑΔΙΚΤΥΟ ΤΩΝ ΠΡΑΓΜΑΤΩΝ
# ΟΜΑΔΙΚΗ ΕΡΓΑΣΤΗΡΙΑΚΗ ΕΡΓΑΣΙΑ
# ΕΞΥΠΝΟΣ ΦΩΤΙΣΜΟΣ

# ΠΑΡΑΤΗΡΗΣΕΙΣ:
# 1) Για την σωστή εκτέλεση, πρέπει πρώτα να εκτελεστεί το DB_init αρχείο που παρέχεται.
# 2) Το debugging της εφαρμογής υλοποιήθηκε με τα simulated uplinks/downlinks που παρέχει το TTN
# 3) Υλοποιήθηκε σε Python 3.10.4

# Υλοποίηση εφαρμογής: Τόμτσης Θωμάς
# Αποστολή σχολίων και παρατηρήσεων: icsd15201@icsd.aegean.gr

import base64
import json
import time
import mysql.connector
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

sleep = 1  # Χρόνος που περιμένω το αποτέλεσμα του callback, συνίσταται να μην αλλαχτεί
light_threshold = 300  # Το threshold πάνω από το οποίο θεωρώ πως είναι επαρκώς φωτισμένη μια περιοχή
flag = 0  # Χρησιμοποιείται έτσι ώστε να μην αποστέλλω στη συσκευή συνεχώς ON/OFF, θα γίνει πιο ξεκάθαρο παρακάτω

# Σύνδεση στη MySQL βάση δεδομένων, θα είχε χρησιμοποιηθεί
# βάση NoSQL που είναι καταλληλότερη αλλά δεν υπήρξε επαρκής χρόνος
# για την εξοικείωση μου με αυτήν, συνεπώς χρησιμοποιήθηκε μια απλή MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="iot",
    password="password",
    database="ttn_msg",
)
cursor = mydb.cursor()


# Υλοποιώ τα callback functions παρακάτω

# Σε περίπτωση σύνδεσης, κάνε subscribe σε όλα τα topics.
# Είναι όλα τα topics που προτείνουν τα docs του TTN
def _on_connect(client, userdata, flags, rc):
    print("Connection Successful")
    if rc == 0:
        print("Subscribing to topics")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/join")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/up")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/queued")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/sent")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/ack")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/nack")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/failed")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/service/data")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/location/solved")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down")
        client.subscribe("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/push")
        time.sleep(sleep)
    elif rc == 1:
        print("Connection refused – incorrect protocol version")
        client.stop_loop()
    elif rc == 2:
        print("Connection refused – invalid client identifier")
        client.stop_loop()
    elif rc == 3:
        print("Connection refused – server unavailable")
        client.stop_loop()
    elif rc == 4:
        print("Connection refused – bad username or password")
        client.stop_loop()
    elif rc == 5:
        print("Connection refused – not authorised")
        client.stop_loop()


# Έλεγχος εάν η αποσύνδεση ήταν επιτυχής
def _on_disconnect(client, userdata, rc):
    if rc == 0:
        print("% Disconnected successfully")
    else:
        print("Application disconnected with code: ", rc)


# Σε περίπτωση λήψης μηνύματος από τον Broker, εγγραφή στην ΒΔ και λήψη απόφασης
def _on_message(client, userdata, msg):
    # Μετατροπή του μηνύματος σε JSON
    payload = str(msg.payload.decode("utf-8"))
    ttn_msg = json.loads(payload)

    # Εξαγωγή της χρήσιμης πληροφορίας από το JSON
    topic = str(msg.topic)

    decoded_payload = ""

    # Εάν το μήνυμα είναι uplink
    if topic == "v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/up":
        device_id = ttn_msg['end_device_ids']['device_id']
        application_id = ttn_msg['end_device_ids']['application_ids']['application_id']
        dev_eui = ttn_msg['end_device_ids']['dev_eui']
        join_eui = ttn_msg['end_device_ids']['join_eui']
        received = ttn_msg['received_at']
        f_port = ttn_msg['uplink_message']['f_port']
        frm_payload = ttn_msg['uplink_message']['frm_payload']
        decoded_payload = base64.b64decode(frm_payload).decode('ascii')

        sql_statement = (
            "INSERT INTO uplink(topic, device_id, application_id, dev_eui, join_eui, received, fport, frm_payload, decoded_payload)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )

        data = (topic, device_id, application_id, dev_eui, join_eui, received, f_port, frm_payload, decoded_payload)

        cursor.execute(sql_statement, data)
        mydb.commit()

    # Εάν το μήνυμα είναι downlink
    elif topic == "v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/queued":
        device_id = ttn_msg['end_device_ids']['device_id']
        application_id = ttn_msg['end_device_ids']['application_ids']['application_id']
        f_port = ttn_msg['downlink_queued']['f_port']

        # Το πεδίο frm_payload δεν υπάρχει στην περίπτωση που το downlink, περιέχει JSON, άρα θα υπάρξει keyerror
        try:
            frm_payload = ttn_msg['downlink_queued']['frm_payload']
            decoded_payload = base64.b64decode(frm_payload).decode('ascii')

            sql_statement = (
                "INSERT INTO downlink(topic, device_id, application_id, fport, frm_payload, decoded_payload)"
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )

            data = (topic, device_id, application_id, f_port, frm_payload, decoded_payload)

            cursor.execute(sql_statement, data)
            mydb.commit()

        except:
            print("json")
            decoded_payload = str(ttn_msg['downlink_queued']['decoded_payload'])

            sql_statement = (
                "INSERT INTO downlink(topic, device_id, application_id, fport, decoded_payload)"
                "VALUES (%s, %s, %s, %s, %s)"
            )

            data = (topic, device_id, application_id, f_port, decoded_payload)

            cursor.execute(sql_statement, data)
            mydb.commit()



    # Εκτύπωση του μηνύματος
    print('% Received New Message:')
    print('% Topic: ' + topic)
    print('% Message Payload: ' + str(msg.payload))
    # ΠΗΓΗ: https://stackoverflow.com/questions/3346824/python-base64-print-problem

    # Λήψη απόφασης, ενεργοποίηση ή απενεργοποίηση του αισθητήρα ;
    # decide(decoded_payload)


# Εμφάνιση του ID του μηνύματος σε περίπτωση που αποστείλουμε εντολή στον Broker
def on_publish(client, userdata, msgID):
    print("% Published with MsgID ", msgID)


# Εφ'όσον κάνουμε subscribe σε ένα topic, ελέγχω εάν είναι επιτυχής η ενέργεια
def on_subscribe(mosq, obj, mid, granted_qos):
    if str(granted_qos) == '(128,)':
        print("Subscription Unsuccessful")
    else:
        print("Subscription successful with QoS level: " + str(granted_qos))


# Ενημέρωση εφ'όσον κάνουμε unsubscribe
def on_unsubscribe():
    print("Unsubscribed from topic")


# Σε περίπτωση log event απλώς τυπώνεται το μήνυμα στην κονσόλα
# Έτσι εμφανίζονται τα ACK messages
def _on_log(client, obj, level, string):
    print('% Log: ', string)


# Αποσύνδεση από το TTN
def disconnect():
    print("% - DISCONNECTING FROM BROKER - %")
    client.disconnect()
    client.loop_stop()


# Σύνδεση στον Broker και αρχικοποίηση του προγράμματος
def _establish_mqtt_connection():
    print('%%% - STARTING CONNECTION - %%%')

    # Στοιχεία σύνδεσης
    Port = 1883
    Broker = 'eu1.cloud.thethings.network'
    username = 'iotlab1@ttn'
    password = 'NNSXS.CN6Q6GOES3FWNF2TKYYOBY6UWUTLKGKF5JWNZFY.G2RHVZ7ABXQFPT5TTONX77SSPNLURFBFGB2AWLIVVUYECU7G7ELQ'

    # Ορίζω τα callback functions
    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_log = _on_log
    client.on_message = _on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe

    # Εκκίνηση της σύνδεσης
    client.username_pw_set(username, password)
    client.connect(Broker, Port)
    time.sleep(sleep)  # Έτσι ώστε το callback να έχει γυρίσει
    client.loop_start()


# Αποστολή εντολής στο TTN
def send_msg(command):
    # AAA= -> 00 00 σε HEX -> TURN LIGHT OFF
    # AQE= -> 01 01 σε HEX -> TURN LIGHT ON
    if command == "OFF":
        publish.single("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/push",
                       '{"downlinks":[{"f_port": 1,"frm_payload":"AAA=","priority": "NORMAL"}]}',
                       hostname="eu1.cloud.thethings.network", port=1883, auth={'username': "iotlab1@ttn1",
                                                                                'password': "NNSXS.CN6Q6GOES3FWNF2TKYYOBY6UWUTLKGKF5JWNZFY.G2RHVZ7ABXQFPT5TTONX77SSPNLURFBFGB2AWLIVVUYECU7G7ELQ"})
    elif command == "ON":
        publish.single("v3/iotlab1@ttn/devices/eui-a8610a3233228f0c/down/push",
                       '{"downlinks":[{"f_port": 1,"frm_payload":"AQE=","priority": "NORMAL"}]}',
                       hostname="eu1.cloud.thethings.network", port=1883, auth={'username': "iotlab1@ttn1",
                                                                                'password': "NNSXS.CN6Q6GOES3FWNF2TKYYOBY6UWUTLKGKF5JWNZFY.G2RHVZ7ABXQFPT5TTONX77SSPNLURFBFGB2AWLIVVUYECU7G7ELQ"})
    else:
        print("% Error: Unknown command provided, cannot publish message")


# Λήψη απόφασης αναφορικά με την μέτρηση
def decide(data):
    # Επειδή η μέθοδος αυτή καλείται με κάθε μέτρηση
    # και θα έστελνε συνεχώς εντολές στον αισθητήρα υλοποιώ ένα flag τέτοιο ώστε:
    # Εάν ο αισθητήρας είναι κλειστός, τότε το flag είναι 1 και σε περίπτωση που η μέτρηση
    # είναι άνω του threshold, δεν θα ξαναστείλω εντολή στον αισθητήρα να ανοίξει ξανά.
    # Αντίστοιχη λογική και για όταν ο αισθητήρας είναι κλειστός
    if data < light_threshold and flag == 0:
        send_msg("ON")
        flag = 1
    elif data >= light_threshold and flag == 1:
        send_msg(("OFF"))
        flag = 0


# Εμφάνιση των περιεχομένων της ΒΔ
def show_db():
    cursor.execute("SELECT * FROM uplink")
    uplinks = cursor.fetchall()
    cursor.execute("SELECT * FROM downlink")
    downlinks = cursor.fetchall()
    print("UPLINK MESSAGES: ")
    for all in uplinks:
        print(all)
    print("DOWNLINK MESSAGES: ")
    for all in downlinks:
        print(all)


# Αρχικοποίηση του client
client = mqtt.Client()

# Σύνδεση στο TTN
_establish_mqtt_connection()

# Loop έως ώτου κλείσουμε την εφαρμογή
try:
    while True:
        time.sleep(sleep)
except KeyboardInterrupt:
    disconnect()
    show_db()
