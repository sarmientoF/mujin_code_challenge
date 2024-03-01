#include <iostream>

using namespace std;

int main(int argc, char const *argv[])
{
    /* code */
    int i = 0;
    int *p = &i;
    int &r = i;

    cout << "i = " << i << endl;
    cout << "p = " << p << endl;
    cout << "r = " << r << endl;
    i++;
    cout << "i = " << i << endl;
    cout << "p = " << p << endl;
    cout << "r = " << r << endl;
    return 0;
}
