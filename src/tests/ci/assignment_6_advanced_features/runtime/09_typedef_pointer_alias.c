typedef int MyInt;
typedef int* IntPtr;

int main() {
    MyInt x = 7;
    IntPtr p = &x;

    return *p;
}