#include <iostream>
#include "EngineCore.h"

int get_itest()
{
#ifdef DEBUGTESTMACRO

	return 114514;

#endif // DEBUGTESTMACRO

	return itest;
}