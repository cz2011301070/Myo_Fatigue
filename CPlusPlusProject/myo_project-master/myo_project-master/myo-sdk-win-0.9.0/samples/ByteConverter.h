#pragma once
/*
* @author changzhuang
* @date 2021.01.16
* @version v1.0
* @brief 
			1. Convert unsigned int, float,double data to byte array
			2. Convert selfdefined class or struct data to byte array
			3. Convert vector, map and list varibles to byte array
			4. Users should define unsigned int index=0
			5. Pack and UnPack data size should less than 4096
			6. Cannot deal with pounsigned inter data
* 
*/
//#include"Dict4Trans.h"
#include<sstream>//lib for type transformation to string
#include<cstring>
#include<string>
//#include<map>
//#include<vector>
//#include<list>
#include<iostream>
using namespace std;


class ByteConverter
{
public:
	//static void mPacking(char* buff, unsigned int& index, const T& value);
	static void mPacking(char* buff, unsigned int& index, const int& value);
	static void mPacking(char* buff, unsigned int& index, const unsigned int& value);
	static void mPacking(char* buff, unsigned int& index, const float& value);
	static void mPacking(char* buff, unsigned int& index, const double& value);
	static void mPacking(char* buff, unsigned int& index, const char& value);
	static void mPacking(char* buff, unsigned int& index, const string& value);
	static void mPacking(char* buff, unsigned int& index, const char*src, unsigned int len_);
	
	static void mUnpacking(const char* buff, unsigned int& index, int& value);
	static void mUnpacking(const char* buff, unsigned int& index, float& value);
	static void mUnpacking(const char* buff, unsigned int& index, double& value);
	static void mUnpacking(const char* buff, unsigned int& index, char& value);
	static void mUnpacking(const char* buff, unsigned int& index, string& value);
	static void mUnpacking(const char* buff, unsigned int& index, string& value, unsigned int len_);
	static void mUnpacking(const char* buff, unsigned int& index, char*dst, unsigned int len_);

};

//template<class KT, class T>
//class Map2Byte : public ByteConverter<T>
//{
//public:
//	static void mPacking(char* buff, unsigned int& index, const map<KT,T>& value);
//	static void mUnpacking(const char* buff, unsigned int& index, map<KT, T>& value);
//	
//};
//
//template<class T>
//class Vector2Byte : public ByteConverter<T>
//{
//public:
//	static void mPacking(char* buff, unsigned int& index, const vector<T> value);
//	static void mUnpacking(const char* buff, unsigned int& index, vector<T>& value);
//};
//
//template<class T>
//class List2Byte : public ByteConverter<T>
//{
//public:
//	static void mPacking(char* buff, unsigned int& index, const list<T> value);
//	static void mUnpacking(const char* buff, unsigned int& index, list<T>& value);
//};


//void ByteConverter::mPacking(char* buff, unsigned int& index, const int& value)
//{
//	unsigned int len = sizeof(value);
//	if (index+len > MAXBUFFERSIZE)
//	{
//		cerr << "ByteConverter<T>::mPacking: buffer exceeding" << endl;
//		exit(1);
//	}
//	else
//	{
//		memcpy_s(&(buff[index]), len, &value, len);
//		index += len;
//	}
//	
//}





