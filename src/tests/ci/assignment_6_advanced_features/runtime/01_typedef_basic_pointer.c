typedef int MyInt;
typedef MyInt* MyIntPtr;

int main() {
    MyInt x = 7;
    MyIntPtr p = &x;
    return *p;
}