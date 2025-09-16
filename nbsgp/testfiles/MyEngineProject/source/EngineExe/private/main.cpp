#include <iostream>
#include "EngineCore.h"

int main()
{
#ifdef SHOPING
	std::cout << "SHOPINGtest" << get_itest();
#else
	std::cout << "test" << get_itest();
#endif // SHOPING
}