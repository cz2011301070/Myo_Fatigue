// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.

// This sample illustrates how to use EMG data. EMG streaming is only supported for one Myo at a time.
#define _TIMESPEC_DEFINED
#include <array>
#include <fstream>
#include <iostream>
#include <cmath>
#include <sstream>
#include <stdexcept>
#include <string>

#include <stdio.h>
#include <myo/myo.hpp>

#include <zmq.h>
#include<assert.h>
#include"ByteConverter.h"
#include<pthread.h>
#include<signal.h>
//#include<errno.h>
//#include<stdio.h>
//#include<Windows.h>


char input;

string state = "";
int MsgCode = 0;
bool IsNetworkPrepared = false;
bool IsThreadkill = false;
class DataCollector : public myo::DeviceListener {
public:

    void addMarker(int type) {
        if (1 == type) {
            marker_amount[0] += 1;
        }
        else if (2 == type) {
            marker_amount[1] += 1;
        }
    }
    void mOnNewMarker()
    {
        mIsNewACCMarker = true;
        mIsNewEMGMarker = true;
        mIsNewGyroMarker = true;
        mIsNewOrientMarker = true;
    }
    void createCsvAcc(std::string filename)
    {
        //Tells DataCollector to create csv file with filename 
        //and remember filename as save location for accelerometer data.
        //Note filename also inclues reletive path to file
        ACCfilename = filename;
        std::fstream ACCfile;
        ACCfile.open(ACCfilename, std::ios_base::out);
        if (!ACCfile.is_open()) {
            std::cout << "failed to create " << ACCfilename << '\n';
            ACC_saving = false;
        }
        else {
            ACCfile << "Timestamp, Acceleration x, Acceleration y, Acceleration z, Marker" << std::endl;
            std::cout << ACCfilename << " created" << std::endl;
        }
    }

    void createCsvEmg(std::string filename)
    {
        //Tells DataCollector to create csv file with filename 
        //and remember filename as save location for emg data.
        //Note filename also inclues reletive path to file
        EMGfilename = filename;
        std::fstream EMGfile;
        EMGfile.open(EMGfilename, std::ios_base::out);
        if (!EMGfile.is_open()) {
            std::cout << "failed to create " << EMGfilename << '\n';
            EMG_saving = false;
        }
        else {
            EMGfile << "Timestamp, Electrode 1, Electrode 2, Electrode 3, Electrode 4, Electrode 5, Electrode 6, Electrode 7, Electrode 8, Marker" << std::endl;
            std::cout << EMGfilename << " created" << std::endl;
        }
    }

    void createCsvGyro(std::string filename)
    {
        //Tells DataCollector to create csv file with filename 
        //and remember filename as save location for gyroscope data.
        //Note filename also inclues reletive path to file
        Gyrofilename = filename;
        std::fstream Gyrofile;
        Gyrofile.open(Gyrofilename, std::ios_base::out);
        if (!Gyrofile.is_open()) {
            std::cout << "failed to create " << Gyrofilename << '\n';
            gyro_saving = false;
        }
        else {
            Gyrofile << "Timestamp, Rotation x, Rotation y, Rotation z, Marker" << std::endl;
            std::cout << Gyrofilename << " created" << std::endl;
        }
    }

    void createCsvOrient(std::string filename)
    {
        //Tells DataCollector to create csv file with filename 
        //and remember filename as save location for orientation data.
        //Note filename also inclues reletive path to file
        Orientfilename = filename;
        std::fstream Orientfile;
        Orientfile.open(Orientfilename, std::ios_base::out);
        if (!Orientfile.is_open()) {
            std::cout << "failed to create " << Orientfilename << '\n';
            orient_saving = false;
        }
        else {
            Orientfile << "Timestamp, Angle x, Angle y, Angle z, Marker" << std::endl;
            std::cout << Orientfilename << " created" << std::endl;
        }
    }

    //onConnect() is called each time a pair myo is connected via Myo Connect
    void onConnect(myo::Myo* myo, uint64_t timestamp, myo::FirmwareVersion firmwareVersion)
    {
        std::cout << "Myo Connection Successful" << '\n';
    }

    // onUnpair() is called whenever the Myo is disconnected from Myo Connect by the user.
    void onUnpair(myo::Myo* myo, uint64_t timestamp)
    {
        // We've lost a Myo.
        // Let's clean up some leftover state.
        emgSamples.fill(0);
        accelSamples.fill(0);
        gyroSamples.fill(0);
        orientSamples.fill(0);
        std::cout << "Myo Unpaired! The program will be closed automatically!"<<endl;
        std::cout << endl;
        exit(1);
    }
    void onDisconnect(myo::Myo* myo, uint64_t timestamp)
    {
        emgSamples.fill(0);
        accelSamples.fill(0);
        gyroSamples.fill(0);
        orientSamples.fill(0);
        std::cout << "Myo Disconnected! The program will be closed automatically!" << endl;
        std::cout << endl;
        exit(1);
    }
    // onAccelerometerData() is called whenever a paired Myo has provided new EMG data, and EMG streaming is enabled.
    void onAccelerometerData(myo::Myo* myo, uint64_t timestamp, const myo::Vector3<float>& accel)
    {
        //Prevents function from recording data before EMG data is recieved.
        //As timestamp is calculated using onEmgData(), this prevents multiple 0 timestamps at start.
        if (collection_start == false) {
            return;
        }

        //Adds the data point timestamp as caluclated by onEmgData() to the ACC_data container for accelerometor data
        ACC_data.append(std::to_string(timestamp_calculated) + ",");

        //Notes how many data points had been recored, this informs program of when to save data
        ACC_recorded += 1;

        //Converts the pointers to data provided by SDK into an array for easier manipulation
        accelSamples[0] = accel.x();
        accelSamples[1] = accel.y();
        accelSamples[2] = accel.z();

        //Adds marker if number of marker required larger than number of markers added
        for (size_t i = 0; i < accelSamples.size(); i++) {
            std::ostringstream oss;
            oss << static_cast<float>(accelSamples[i]);
            std::string accString = oss.str();
            ACC_data.append(accString + ",");
        }

        //Adds marker if number of marker required larger than number of markers added
        mIsNewACCMarker ? ACC_data.append(std::to_string(MsgCode)) : ACC_data.append("0");
        mIsNewACCMarker = false; // this state will be changed when new msg comes
        ACC_data.append("\n");

        //Saves the data in ACC_data into the selected CSV file
        //Saving only occures every 50 data points for performance reasons
        if (ACC_recorded > 50) {
            std::fstream ACC_out;
            ACC_out.open(ACCfilename, std::ios_base::app);
            if (!ACC_out.is_open()) {
                ACC_saving = false;
            }
            else {
                ACC_out << ACC_data;
            }
            //Resets the counter and emties the temporary container for accelerometer data
            ACC_recorded = 0;
            ACC_data = "";
        }

    }

    // onEmgData() is called whenever a paired Myo has provided new EMG data, and EMG streaming is enable
    void onEmgData(myo::Myo* myo, uint64_t timestamp, const int8_t* emg)
    {
        //Allows data collection to start onece emg data is recieved
        if (collection_start == false) {
            collection_start = true;
        }

        //Data correction mechenism - functionally similar as the one used in MyoMex
        if (EMG_timestamp_repeat == true) {
            //A quirk of myo SDK is it sends pairs of data with same system timestamps
            //If a data point does not come with it's pair, them we know a data point is missing
            if (EMG_last_timestamp != timestamp) {
                //Duplicates the known data point in the pair as placeholder for the unknown datapoint
                EMG_data.append(std::to_string(timestamp_calculated) + ",");
                timestamp_calculated += 5;
                EMG_data.append(EMG_tmp);
                //Records that above duplication had occured, this info will be made known to user in print() 
                lines_duplicated += 1;
            }
            //Once the system timestamp had repeated once, we expect next data point to have different timestamp
            EMG_timestamp_repeat = false;
        }
        else {
            //If last timestamp is not expected to repeat, then we expect next timestamp to repeat
            EMG_timestamp_repeat = true;

            //Records current system timestamp so we can compare the next system timestamp with it
            EMG_last_timestamp = timestamp;
        }

        //The recorded timestamp is calculated, we assume emg data is actually recorded in perfect 5 ms intervals
        //and all inperfections in system timestamp is due to how system records time
        //The same method is also used in MyoMex
        EMG_data.append(std::to_string(timestamp_calculated) + ",");
        timestamp_calculated += 5;

        //Notes how many emg data points had been recored, this informs program of when to save data
        EMG_recorded += 1;

        //EMG_tmp holds emg values from last data point for data correction mechenism
        //Data from last time onEmgData() was called is emptied here to recieve current data for next cycle
        EMG_tmp = "";

        //Converts the pointers to emg data provided by SDK into an array for easier manipulation
        for (int i = 0; i < 8; i++) {
            emgSamples[i] = emg[i];
        }

        //Converts emgSamples array into a string with CSV compatible formatting stored in EMG_tmp
        for (size_t i = 0; i < emgSamples.size(); i++) {
            std::ostringstream oss;
            oss << static_cast<float>(emgSamples[i]);
            std::string emgString = oss.str();
            EMG_tmp.append(emgString + ',');
        }

        //Adds marker if number of marker required larger than number of markers added
        // when new marker comes, stored in MsgCode
        mIsNewEMGMarker ? EMG_tmp.append(std::to_string(MsgCode)) : EMG_tmp.append("0");
        mIsNewEMGMarker = false; // this state will be changed when new msg comes
        EMG_tmp.append("\n");

        //Adds this data point as a new line to EMG_data, which records all string data awaiting output to CSV
        EMG_data.append(EMG_tmp);

        //Saves the data in EMG_data into the selected CSV file
        //Saving only occures every 200 data points for performance reasons
        if (EMG_recorded > 200) {
            std::fstream EMG_out;
            EMG_out.open(EMGfilename, std::ios_base::app);
            if (!EMG_out.is_open()) {
                EMG_saving = false;
            }
            else {
                EMG_out << EMG_data;
            }
            //Resets the counter and emties the temporary container for emg data
            EMG_recorded = 0;
            EMG_data = "";
        }
    }

    void onGyroscopeData(myo::Myo* myo, uint64_t timestamp, const myo::Vector3<float>& gyro)
    {
        //Prevents function from recording data before EMG data is recieved.
        //As timestamp is calculated using onEmgData(), this prevents multiple 0 timestamps at start.
        if (collection_start == false) {
            return;
        }

        //Adds the data point timestamp as caluclated by onEmgData() to the ACC_data container for gyroscope data
        gyro_data.append(std::to_string(timestamp_calculated) + ",");

        //Notes how many data points had been recored, this informs program of when to save data
        gyro_recorded += 1;

        //Converts the pointers to data provided by SDK into an array for easier manipulation
        gyroSamples[0] = gyro.x();
        gyroSamples[1] = gyro.y();
        gyroSamples[2] = gyro.z();

        //Converts gyroSamples array into a string with CSV compatible formatting stored in gyro_data container
        for (size_t i = 0; i < gyroSamples.size(); i++) {
            std::ostringstream oss;
            oss << static_cast<float>(gyroSamples[i]);
            std::string gyroString = oss.str();
            gyro_data.append(gyroString + ",");
        }
        //Adds marker if number of marker required larger than number of markers added
        mIsNewGyroMarker ? gyro_data.append(std::to_string(MsgCode)) : gyro_data.append("0");
        mIsNewGyroMarker = false; // this state will be changed when new msg comes
        gyro_data.append("\n");

        //Saves the data in gyro_data into the selected CSV file
        //Saving only occures every 50 data points recored for performance reasons
        if (gyro_recorded > 50) {
            std::fstream gyro_out;
            gyro_out.open(Gyrofilename, std::ios_base::app);

            if (!gyro_out.is_open()) {
                gyro_saving = false;
            }
            else {
                gyro_out << gyro_data;
            }
            //Resets the counter and emties the temporary container for gyroscope data
            gyro_recorded = 0;
            gyro_data = "";
        }
    }

    void onOrientationData(myo::Myo* myo, uint64_t timestamp, const myo::Quaternion<float>& quat)
    {
        //Namespaces for math functions
        using std::atan2;
        using std::asin;
        using std::sqrt;
        using std::max;
        using std::min;

        //Prevents function from recording data before EMG data is recieved.
        //As timestamp is calculated using onEmgData(), this prevents multiple 0 timestamps at start.
        if (collection_start == false) {
            return;
        }

        //Adds the data point timestamp as caluclated by onEmgData() to the ACC_data container for gyroscope data
        orient_data.append(std::to_string(timestamp_calculated) + ",");

        //Notes how many data points had been recored, this informs program of when to save data
        orient_recorded += 1;

        // Calculate Euler angles (roll, pitch, and yaw) from the unit quaternion.
        orientSamples[0] = atan2(2.0f * (quat.w() * quat.x() + quat.y() * quat.z()),
            1.0f - 2.0f * (quat.x() * quat.x() + quat.y() * quat.y()));

        orientSamples[1] = asin(max(-1.0f, min(1.0f, 2.0f * (quat.w() * quat.y() - quat.z() * quat.x()))));

        orientSamples[2] = atan2(2.0f * (quat.w() * quat.z() + quat.x() * quat.y()),
            1.0f - 2.0f * (quat.y() * quat.y() + quat.z() * quat.z()));

        //Converts orientSamples array into a string with CSV compatible formatting stored in orient_data container
        for (size_t i = 0; i < orientSamples.size(); i++) {
            std::ostringstream oss;
            oss << static_cast<float>(orientSamples[i]);
            std::string orientString = oss.str();
            orient_data.append(orientString + ",");
        }
        //Adds marker if number of marker required larger than number of markers added
        mIsNewOrientMarker ? orient_data.append(std::to_string(MsgCode)) : orient_data.append("0");
        mIsNewOrientMarker = false; // this state will be changed when new msg comes
        orient_data.append("\n");

        //Saves the data in orient_data into the selected CSV file
        //Saving only occures every 50 data points recored for performance reasons
        if (orient_recorded > 50) {
            std::fstream orient_out;
            orient_out.open(Orientfilename, std::ios_base::app);
            if (!orient_out.is_open()) {
                orient_saving = false;
            }
            else {
                orient_out << orient_data;
            }
            //Resets the counter and emties the temporary container for orientation data
            orient_recorded = 0;
            orient_data = "";
        }
    }
    
    void statemoniter()
    {
        cout << "******************Data Saving State********************************************" << endl;
        //emg
        if (EMG_saving == true) {
            //When data saving is normal, informs the user if data had been modified by correction mechenism
            if (lines_duplicated > 0 && EMG_saving == true) {
                std::cout << " " << lines_duplicated << " line(s) of problematic data!"<<endl;
            }
            else {
                std::cout << "EMG data saving normal"<<endl;
            }
        }
        else {
            std::cout << " ***EMG data saving failed!***"<<endl;
        }
        //acc
        if (ACC_saving == true) {
            std::cout << "ACC data saving normal"<<endl;
        }
        else {
            std::cout << "***ACC  data saving failed!***"<<endl;
        }

        //gyro
        if (gyro_saving == true) {
            std::cout << " Gyro data saving normal"<<endl;
        }
        else {
            std::cout << "***Gyro data saving failed!***"<<endl;
        }

        //orientation
        if (orient_saving == true) {
            std::cout << "Orientation data saving normal"<<endl;
        }
        else {
            std::cout << " ***Orientation data saving failed!***"<<endl;
        }
    }
    void print() {
        //Inhibits outputing meaningless data when collection had not started
        if (collection_start == false) {
            return;
        }

        //Deletes last 5 lines of output so data output is not a mess
        for (int i = 0; i < 5; i++) {
            std::cout << "\x1b[1A" << "\x1b[2K";
        }

        //Line for emg data output
        std::cout << "          EMG data:";
        for (size_t i = 0; i < emgSamples.size(); i++) {
            //Outputs data from last time onEmgData() was called
            //Note console output is a snapshot of one particular time point rather than some average over time
            std::ostringstream oss;
            oss << static_cast<float>(emgSamples[i]);
            std::string emgString = oss.str();
            std::cout << '[' << emgString << std::string(4 - emgString.size(), ' ') << ']';
        }
        //Informs the user if data saving is occuring correctly
        if (EMG_saving == true) {
            //When data saving is normal, informs the user if data had been modified by correction mechenism
            if (lines_duplicated > 0 && EMG_saving == true) {
                std::cout << " " << lines_duplicated << " line(s) of problematic data!";
            }
            else {
                std::cout << " data saving normal";
            }
        }
        else {
            std::cout << " ***data saving failed!***";
        }

        //Adds new line for next row of output
        std::cout << "\n";

        //Line for Accelerometer data output
        std::cout << "Accelerometer data:";
        //Outputs data from last time onAccelerometerData() was called
        for (size_t i = 0; i < accelSamples.size(); i++) {
            //Rounding to provide a neat console output
            float tmp;
            tmp = accelSamples[i] * 1000;
            tmp = round(tmp);
            tmp = tmp / 1000;
            std::string accelString = std::to_string(tmp);
            accelString = accelString.substr(0, accelString.size() - 3);
            std::cout << '[' << accelString << std::string(10 - accelString.size(), ' ') << ']';
        }
        //Informs the user if data saving is occuring correctly
        if (ACC_saving == true) {
            std::cout << "             data saving normal";
        }
        else {
            std::cout << "             ***data saving failed!***";
        }
        //Adds new line for next row of output
        std::cout << "\n";

        //Line for Gyroscope data output
        std::cout << "    Gyroscope data:";
        //Outputs data from last time onGyroscopeData() was called
        for (size_t i = 0; i < gyroSamples.size(); i++) {
            //Rounding to provide a neat console output
            float tmp;
            tmp = gyroSamples[i] * 1000;
            tmp = round(tmp);
            tmp = tmp / 1000;
            std::string gyroString = std::to_string(tmp);
            gyroString = gyroString.substr(0, gyroString.size() - 3);
            std::cout << '[' << gyroString << std::string(10 - gyroString.size(), ' ') << ']';
        }
        //Informs the user if data saving is occuring correctly
        if (gyro_saving == true) {
            std::cout << "             data saving normal";
        }
        else {
            std::cout << "             ***data saving failed!***";
        }
        //Adds new line for next row of output
        std::cout << "\n";

        //Line for Orientation data output
        std::cout << "  Orientation data:";
        for (size_t i = 0; i < orientSamples.size(); i++) {
            //Rounding to provide a neat console output
            float tmp;
            tmp = orientSamples[i] * 1000;
            tmp = round(tmp);
            tmp = tmp / 1000;
            std::string orientString = std::to_string(tmp);
            orientString = orientString.substr(0, orientString.size() - 3);
            std::cout << '[' << orientString << std::string(10 - orientString.size(), ' ') << ']';
        }
        //Informs the user if data saving is occuring correctly
        if (orient_saving == true) {
            std::cout << "             data saving normal";
        }
        else {
            std::cout << "             ***data saving failed!***";
        }
        //Adds new line for next row of output
        std::cout << "\n";

        //Output for time counter
        float output_time;
        float float_time = timestamp_calculated;

        //Converts miliseconds into seconds
        output_time = float_time / 1000;
        std::string output_string = std::to_string(output_time);

        //Outputs the timestamp in seconds with trailing zeros removed
        std::cout << "      Elapsed time:" << output_string.substr(0, output_string.size() - 3) << "\n";

    }

    // Initializing variables
    bool collection_start = false;
    int timestamp_calculated = 0;
    std::array<int, 2> marker_amount = { 0, 0 };

    //Recording accelerometor data
    std::array<float, 3> accelSamples = { 0, 0, 0 };
    std::string ACC_data;
    bool ACC_saving = true;
    int ACC_recorded = 0;
    std::array<int, 2> ACC_marker = { 0, 0 };
    bool mIsNewACCMarker = false;

    //Recording EMG data
    std::array<int8_t, 8> emgSamples = { 0, 0, 0, 0, 0, 0, 0, 0 };
    std::string EMG_data;
    std::string EMG_tmp;
    uint64_t EMG_last_timestamp = 0;
    bool EMG_saving = true;
    bool EMG_timestamp_repeat = false;
    int EMG_recorded = 0;
    int lines_duplicated = 0;
    std::array<int, 2> EMG_marker = { 0, 0 };
    bool mIsNewEMGMarker = false;

    //Recording gyroscope data
    std::array<float, 3> gyroSamples = { 0, 0, 0 };
    std::string gyro_data;
    bool gyro_saving = true;
    int gyro_recorded = 0;
    std::array<int, 2> gyro_marker = { 0, 0 };
    bool mIsNewGyroMarker = false;

    //Recording orientation data
    std::array<float, 3> orientSamples = { 0, 0, 0 };
    std::string orient_data;
    bool orient_saving = true;
    int orient_recorded = 0;
    std::array<int, 2> orient_marker = { 0, 0 };
    bool mIsNewOrientMarker = false;

    //File names
    std::string ACCfilename;
    std::string EMGfilename;
    std::string Gyrofilename;
    std::string Orientfilename;

    //monitor state
    bool IsStatePrinted = false;
};
DataCollector collector;
static void* subThread(void*)
{
    void* context = zmq_ctx_new();
    void* subscriber = zmq_socket(context, ZMQ_SUB);
    zmq_connect(subscriber, "tcp://127.0.0.1:5671");
    zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "TASK_START", 1);
    zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "TASK_STOP", 1);
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
        cout << "Thread: " << client_id << endl;
        index_clientid = 0;
        state = client_id;
        zmq_msg_close(&clientid_msg);
    }
    return NULL;
}
static void* DealerThread(void*)
{
    void* context = zmq_ctx_new();
    void* frontend = zmq_socket(context, ZMQ_ROUTER);

    string IP_Address = "127.0.0.1";
    string nettype = "tcp";
    string port_frontend = "5671";
    string addr_front = (nettype + "://" + IP_Address + ":" + port_frontend);
    const char* addr_frontend = addr_front.c_str();

    int msgCounter = 0;
#if (defined (WIN32))
    zmq_bind(frontend, addr_frontend); // frontend
#else
    zmq_bind(frontend, "ipc://frontend.ipc");
#endif
    //std::multimap<string, int> workers;//should be replaced by queue
    //std::multimap<string, int> clients;

    while (1) {
        zmq_pollitem_t items[] = {
                { frontend, 0, ZMQ_POLLIN, 0 }
        };

        int rc = zmq_poll(items, 1, -1);
        if (rc == -1)
            break;
        //frontend-client
        if (items[0].revents & ZMQ_POLLIN)
        {

            // Part1: recv client id
            zmq_msg_t clientid_msg;
            int rc = zmq_msg_init(&clientid_msg);
            assert(rc == 0);
            /* Block until a message is available to be received from socket */
            rc = zmq_msg_recv(&clientid_msg, frontend, 0);
            assert(rc != -1);
            int clientid_len = zmq_msg_size(&clientid_msg);
            string client_id;
            unsigned int index_clientid = 0;
            ByteConverter::mUnpacking((char*)zmq_msg_data(&clientid_msg), index_clientid, client_id, clientid_len);
            index_clientid = 0;
            zmq_msg_close(&clientid_msg);
            

            //Part2: recv delimeter
            char* delimeter_buf = new char[1];
            int empty = zmq_recv(frontend, delimeter_buf, 1, 0);


            //Part3: recv message_len--contains the message
            int len = sizeof(int);
            char* message_len = new char[len];
            int request_len = zmq_recv(frontend, message_len, len, 0);
            assert(request_len != -1);
            //parse message_len
            unsigned int index = 0;
            int message_length = 0;
            ByteConverter::mUnpacking(message_len, index, message_length);
            
            if (message_len != nullptr)
            {
                delete[] message_len;
                message_len = nullptr;
            }
            if (delimeter_buf != nullptr)
            {
                delete[] delimeter_buf;
                delimeter_buf = nullptr;
            }

            if (message_length == 100)//this 200 is set to detect whether the client can successfully send the data
            {
                //cout << "Network setup successfully!" << endl;
                msgCounter++;
                if (msgCounter == 5)//decided by unity side
                {
                    IsNetworkPrepared = true;
                    msgCounter = 0;
                }
            }
            else if (message_length == 200)
            {
                msgCounter++;
                if (msgCounter == 5)//decided by unity side
                {
                    msgCounter = 0;
                    zmq_close(frontend);
                    //zmq_close(backend);
                    zmq_ctx_destroy(context);
                    IsThreadkill = true;
                    pthread_exit("Exit thread");//stop calling the thread
                }
                
            }
            else
            {
                std::cout << "\n\n\n\n\n";
                cout << client_id<< ": " << message_length << endl;
                MsgCode = message_length;
                collector.mOnNewMarker();
            }
            
            ////// Part4: string
            //char* Msg = new char[message_length];
            //rc = zmq_recv(frontend, Msg, message_length, 0);
            //assert(rc != -1);
            //unsigned int contentIndex = 0;
            //string content;
            //ByteConverter::mUnpacking(Msg, contentIndex, content, message_length);

            //std::cout << content << endl;
            //state = content;

            //if (Msg != nullptr)
            //{
            //    delete[] Msg;
            //    Msg = nullptr;
            //}
            

        }


    }
    zmq_close(frontend);
    //zmq_close(backend);
    zmq_ctx_destroy(context);
    pthread_exit("Exit thread");//stop calling the thread
    return 0;
}

int RunMyo(pthread_t* threadid)
{
    // We catch any exceptions that might occur below -- see the catch statement for more details.
    try {

        // First, we create a Hub with our application identifier. Be sure not to use the com.example namespace when
        // publishing your application. The Hub provides access to one or more Myos.
        myo::Hub hub("com.example.emg-data-sample");

        std::cout << "Attempting to find a Myo..." << std::endl;

        // Next, we attempt to find a Myo to use. If a Myo is already paired in Myo Connect, this will return that Myo
        // immediately.
        // waitForMyo() takes a timeout value in milliseconds. In this case we will try to find a Myo for 10 seconds, and
        // if that fails, the function will return a null pointer.
        myo::Myo* myo = hub.waitForMyo(10000);

        // If waitForMyo() returned a null pointer, we failed to find a Myo, so exit with an error message.
        if (!myo) {
            throw std::runtime_error("Unable to find a Myo!");
        }

        // We've found a Myo.
        std::cout << "Connected to a Myo armband!" << std::endl << std::endl;

        // Next we enable EMG streaming on the found Myo.
        myo->setStreamEmg(myo::Myo::streamEmgEnabled);

        // Next we construct an instance of our DeviceListener, so that we can register it with the Hub.


        // Hub::addListener() takes the address of any object whose class inherits from DeviceListener, and will cause
        // Hub::run() to send events to all registered device listeners.
        hub.addListener(&collector);

        // Creates the CSV files for data saving, this will overide any existing files
        collector.createCsvAcc("Output/Accelerometer.csv");
        collector.createCsvEmg("Output/EMG.csv");
        collector.createCsvGyro("Output/Gyroscope.csv");
        collector.createCsvOrient("Output/Orientation.csv");

        // Quick and dirty way of preventing previous consol output from deleted by print()
        std::cout << "\n\n\n\n\n";

        // Initializes couter for console output
        int counter = 0;

        // Finally we enter our main loop.
        while (1) {

            if (IsNetworkPrepared)
            {
                cout << "Network connected!" << endl;
                std::cout << "\n\n\n\n\n"; //Quick and dirty way of preventing previous consol output from deleted by print() 
                IsNetworkPrepared = false;
            }
            if (IsThreadkill)
            {
                pthread_kill(*threadid, SIGABRT_COMPAT);
                IsThreadkill = false;
                return 0;
            }
            
            // In each iteration of our main loop, we run the Myo event loop for a set number of milliseconds.
            // In this case, we wish to update our display 50 times a second, so we run for 1000/20 milliseconds.
            hub.runOnce(10);

            // Updates the console output using data recieved at this moment 
            // This is only done every 30 cycles of the main loop to improve legibility

            /*if (!collector.IsStatePrinted)
            {*/
            if (counter > 30) {
                collector.print();
                //collector.statemoniter();
                counter = 0;
                //collector.IsStatePrinted = true;
            }
            counter += 1;
            //}
            
        }
        
    }
    // If a standard exception occurred, we print out its message and exit.
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        std::cerr << "Press enter to continue.";
        std::cin.ignore();
        return 1;
    }
}

int main(int argc, char** argv)
{
    pthread_t pthreadid;
    pthread_create(&pthreadid, NULL, DealerThread, NULL);
    RunMyo(&pthreadid);
    return 0;
}
