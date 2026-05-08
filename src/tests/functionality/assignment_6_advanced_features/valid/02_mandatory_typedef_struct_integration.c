#include <stdio.h>

typedef int MyInt;
typedef float MyFloat;
typedef char MyChar;

typedef int* IntPtr;

struct Point {
    int x;
    int y;
};

typedef struct Point Point;

int main() {
    MyInt a = 42;
    MyFloat b = 3.14f;
    MyChar c = 'z';

    MyInt arr[3];
    arr[0] = 1;
    arr[1] = 2;
    arr[2] = 3;

    Point p;
    p.x = 10;
    p.y = 20;

    MyInt result = a + arr[0];
    printf("%d\n", result);

    return 0;
}