# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.
!pip install awscrt
!pip install awsiotsdk
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import sys
import threading
import boto3
import time
import json


# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the device connects to the server,
# subscribes to a topic, and begins publishing messages to that topic.
# The device should receive those same messages back from the message broker,
# since it is subscribed to that same topic.

# cmdData is the arguments/input from the command line placed into a single struct for
# use in this sample. This handles all of the command line parsing, validating, etc.
# See the Utils/CommandLineUtils for more information.


received_count = 0
received_all_event = threading.Event()

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))

    content = payload
    wiadomosc = str(payload)
    splited = wiadomosc.split(',')
    filename = f"core2/day:{splited[5]}/hour:{splited[6]}/{splited[7]}:{splited[8]}.json"
    
    s3.Object('iotstorage180281', filename).put(Body=content)

# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error))

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")

if __name__ == '__main__':
    # Create the proxy options if the data is present in cmdData
    proxy_options = None
    # if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
    #     proxy_options = http.HttpProxyOptions(
    #         host_name=cmdData.input_proxy_host,
    #         port=cmdData.input_proxy_port)

    # Create a MQTT connection from the command line data
    s3 = boto3.resource(
        's3',
        region_name='us-east-1',
        aws_access_key_id=None,
        aws_secret_access_key=None
    )
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint="a2pvn903w589z0-ats.iot.us-east-1.amazonaws.com",
        port=8883,
        cert_filepath="b2c1abe19efc8c3cb6c9f15281ea59e8e1d06389836e7ec7d369bf783730271a-certificate.pem.crt",
        pri_key_filepath="b2c1abe19efc8c3cb6c9f15281ea59e8e1d06389836e7ec7d369bf783730271a-private.pem.key",
        ca_filepath="AmazonRootCA1.pem",
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id="serwerlokalny",
        clean_session=False,
        keep_alive_secs=30,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed)

    # if not cmdData.input_is_ci:
    #     print(f"Connecting to {cmdData.input_endpoint} with client ID '{cmdData.input_clientId}'...")
    # else:
    #     print("Connecting to endpoint with client ID")
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    message_topic = "core2"

    # Subscribe
    print("Subscribing to topic '{}'...".format(message_topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=message_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")