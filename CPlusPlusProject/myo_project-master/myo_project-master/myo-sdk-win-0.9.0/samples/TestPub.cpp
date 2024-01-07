
#define _TIMESPEC_DEFINED
#include <zmq.h>
#include<iostream>
#include<assert.h>
#include"ByteConverter.h"
#include<pthread.h>
using namespace std;
string state = "";
static void* subThread(void*)
{
    void* context = zmq_ctx_new();
    void* subscriber = zmq_socket(context, ZMQ_SUB);
    zmq_connect(subscriber, "tcp://192.168.43.238:5671");
    zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "TASK_START", 1);
    while (true)
    {
        // Part1: recv client id
        zmq_msg_t clientid_msg;
        int rc = zmq_msg_init(&clientid_msg);
        assert(rc == 0);
        /* Block until a message is available to be received from socket */
        rc = zmq_msg_recv(&clientid_msg, subscriber, 0);
        assert(rc != -1);
        int clientid_len = zmq_msg_size(&clientid_msg);
        string client_id;
        unsigned int index_clientid = 0;
        ByteConverter::mUnpacking((char*)zmq_msg_data(&clientid_msg), index_clientid, client_id, clientid_len);
        cout << "Thread: "<<client_id << endl;
        index_clientid = 0;
        state = client_id;
        zmq_msg_close(&clientid_msg);
    }
    return NULL;
}
int main()
{
    pthread_t pthreadid;
    pthread_create(&pthreadid, NULL, subThread, NULL);
    
    while (true)
    {
        if (state != "")
        {
            cout << "MainThread: " << state << endl;
            state = "";
        }
    }
	return 0;
}
