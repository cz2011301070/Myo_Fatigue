#include"ByteConverter.h"

void ByteConverter::mPacking(char* buff, unsigned int& index, const int& value)
{
	unsigned int len = sizeof(value);

	memcpy_s(&(buff[index]), len, &value, len);
	index += len;

}
void ByteConverter::mPacking(char* buff, unsigned int& index, const unsigned int& value)
{
	unsigned int len = sizeof(value);

	memcpy_s(&(buff[index]), len, &value, len);
	index += len;

}
void ByteConverter::mPacking(char* buff, unsigned int& index, const float& value)
{
	unsigned int len = sizeof(value);

	memcpy_s(&(buff[index]), len, &value, len);
	index += len;


}
void ByteConverter::mPacking(char* buff, unsigned int& index, const double& value)
{
	unsigned int len = sizeof(value);
	
	memcpy_s(&(buff[index]), len, &value, len);
	index += len;


}
void ByteConverter::mPacking(char* buff, unsigned int& index, const char& value)
{
	unsigned int len = sizeof(value);
	
	memcpy_s(&(buff[index]), len, &value, len);
	index += len;
	

}
void ByteConverter::mPacking(char* buff, unsigned int& index, const string& value)
{
	int len_ = value.length();
	
	mPacking(buff, index, len_);
	memcpy_s(&(buff[index]), len_, value.data(), len_);
	index += len_;
}
void ByteConverter::mPacking(char* buff, unsigned int& index, const char* src, unsigned int len_)
{
	if (src != nullptr)
	{
		memcpy_s(&buff[index], len_, src, len_);
		index += len_;
	}
}


void ByteConverter::mUnpacking(const char* buff, unsigned int& index, int& value)
{
	unsigned int len_ = sizeof(value);
	if (buff == nullptr)
	{
		return;
	}
	else
	{
		memcpy_s(&value, len_, &(buff[index]), len_);
		index += len_;
	}
	
}
void ByteConverter::mUnpacking(const char* buff, unsigned int& index, float& value)
{
	unsigned int len_ = sizeof(value);

	memcpy_s(&value, len_, &(buff[index]), len_);
	index += len_;


}
void ByteConverter::mUnpacking(const char* buff, unsigned int& index, double& value)
{
	unsigned int len_ = sizeof(value);
	memcpy_s(&value, len_, &(buff[index]), len_);
	index += len_;

}
void ByteConverter::mUnpacking(const char* buff, unsigned int& index, char& value)
{
	unsigned int len_ = sizeof(value);
	
	memcpy_s(&value, len_, &(buff[index]), len_);
	index += len_;
	

}
void ByteConverter::mUnpacking(const char* buff, unsigned int& index, string& value)
{
	int len_ = 0;
	mUnpacking(buff, index, len_);

	try
	{
		char* temp = new char[len_+1];
		memcpy_s(temp, len_, &(buff[index]), len_);
		if (temp != nullptr)
		{
			temp[len_] = '\0';
			value = temp;//deep copy
		}
		delete[] temp;
		temp = nullptr;
		index += len_;
	}
	catch(exception e)
	{
		cerr << "ByteConverter<T>::mUnpacking: no data is copied" << endl;
		exit(1);
	}

	

}
void ByteConverter::mUnpacking(const char* buff, unsigned int& index, string& value, unsigned int len_)
{

	char *temp=new char[len_+1];
	//char *temp=new char[len_];
	memcpy_s(temp , len_, &(buff[index]), len_);
	if (temp != nullptr)
	{
		temp[len_] = '\0';
		value = temp;//deep copy
	}
	delete[] temp;
	temp = nullptr;
	index += len_;
}
void ByteConverter::mUnpacking(const char* buff, unsigned int& index, char* dst, unsigned int len_)
{
	if (buff != nullptr)
	{
		memcpy_s(dst, len_, &(buff[index]), len_);
		index += len_;
	}
	
}
//template<class KT, class T>
//void Map2Byte<KT,T>::mPacking(char* buff, unsigned int& index, const map<KT, T>& value)
//{
//	if (index > MAXBUFFERSIZE)
//	{
//		cerr << "Map2Byte<KT,T>::mPacking: Packed data bigger than MAXBUFFERSIZE" << endl;
//		exit(1);
//	}
//	else
//	{
//		map<KT, T>::const_iterator it = value.begin();
//		while (it != value.end())
//		{
//			memcpy_s(&(buff[index]), sizeof(KT), &(it->first), sizeof(KT));
//			index += sizeof(KT);
//
//			memcpy_s(&(buff[index]), sizeof(T), &(it->second), sizeof(T));
//			index += sizeof(T);
//
//			it++;
//			
//		}
//		
//		
//	}
//}
//
//template<class KT, class T>
//void Map2Byte<KT, T>::mUnpacking(const char* buff, unsigned int& index, map<KT, T>& value)
//{
//	if (index > MAXBUFFERSIZE)
//	{
//		cerr << "Map2Byte<KT,T>::mPacking: Packed data bigger than MAXBUFFERSIZE" << endl;
//		exit(1);
//	}
//	else
//	{
//		KT keyTemp;
//		T valueTemp;
//		memcpy_s(&keyTemp, sizeof(KT), &(buff[index]), sizeof(KT));
//		index += sizeof(KT);
//		
//		memcpy_s(&valueTemp, sizeof(T), &(buff[index]), sizeof(T));
//		index += sizeof(T);
//
//		value[keyTemp] = valueTemp;
//
//	}
//}
//
//template<class T>
//void Vector2Byte<T>::mPacking(char* buff, unsigned int& index, const vector<T> value)
//{
//	if (index > MAXBUFFERSIZE)
//	{
//		cerr << "Vector2Byte<T>::mPacking: Packed data bigger than MAXBUFFERSIZE" << endl;
//		exit(1);
//	}
//	else
//	{
//		vector<T>::const_iterator it = value.begin();
//		while (it != value.end())
//		{
//			memcpy_s(&(buff[index]), sizeof(T), &(*it), sizeof(T));
//			index += sizeof(T);
//
//			it++;
//
//		}
//
//	}
//}
//
//template<class T>
//void Vector2Byte<T>::mUnpacking(const char* buff, unsigned int& index, vector<T>& value)
//{
//	if (index > MAXBUFFERSIZE)
//	{
//		cerr << "Vector2Byte<T>::mUnpacking: Packed data bigger than MAXBUFFERSIZE" << endl;
//		exit(1);
//	}
//	else
//	{
//		T valueTemp;
//		
//		memcpy_s(&valueTemp, sizeof(T), &(buff[index]), sizeof(T));
//		index += sizeof(T);
//
//		value.push_back(valueTemp);
//
//	}
//}
//
//template<class T>
//void List2Byte<T>::mPacking(char* buff, unsigned int& index, const list<T> value)
//{
//	if (index > MAXBUFFERSIZE)
//	{
//		cerr << "List2Byte<T>::mPacking: Packed data bigger than MAXBUFFERSIZE" << endl;
//		exit(1);
//	}
//	else
//	{
//		list<T>::const_iterator it = value.begin();
//		while (it != value.end())
//		{
//			memcpy_s(&(buff[index]), sizeof(T), &(*it), sizeof(T));
//			index += sizeof(T);
//
//			it++;
//
//		}
//
//	}
//}
//
//template<class T>
//void List2Byte<T>::mUnpacking(const char* buff, unsigned int& index, list<T>& value)
//{
//	if (index > MAXBUFFERSIZE)
//	{
//		cerr << "List2Byte<T>::mUnpacking: Packed data bigger than MAXBUFFERSIZE" << endl;
//		exit(1);
//	}
//	else
//	{
//		T valueTemp;
//
//		memcpy_s(&valueTemp, sizeof(T), &(buff[index]), sizeof(T));
//		index += sizeof(T);
//
//		value.push_back(valueTemp);
//
//	}
//}
//template <class T>
//void ByteConverter<T>::mPacking(char* buff, int& index, const T value)
//{
//	char* buffer = new char();
//	stringstream temp;
//	temp << value;
//	temp >> buffer;
//
//	memcpy_s(buff, index+sizeof(value), buffer, sizeof(value));
//
//	delete buffer;
//	buffer = NULL;
//
//}
//template <class T>
//void ByteConverter<T>::mUnpacking(char* buff, int& index, T& value)
//{
//	char* buffer = new char();
//	memcpy_s(buffer, sizeof(index), buff, index + sizeof(index));
//
//}
