/*
 * LLVM codegen showcase
 * This file is meant to test LLVM generation and runtime behavior.
 */

typedef int MyInt;

struct Point {
    int x;
    int y;
};

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    int result = 0;
    int i = 0;

    while (i < b) {
        result = result + a;
        i = i + 1;
    }

    return result;
}

int sum_array(int* arr, int size) {
    int i = 0;
    int total = 0;

    while (i < size) {
        total = total + arr[i];
        i = i + 1;
    }

    return total;
}

int use_point(struct Point* p) {
    return p->x + p->y;
}

int main() {
    MyInt values[3] = {1, 2, 3};
    struct Point p;

    int array_sum = 0;
    int point_sum = 0;
    int multiplied = 0;
    int result = 0;

    p.x = 4;
    p.y = 5;

    array_sum = sum_array(values, 3);
    point_sum = use_point(&p);
    multiplied = multiply(2, 3);

    result = add(array_sum, point_sum);
    result = result + multiplied;

    if (result > 20) {
        result = result - 1;
    } else {
        result = result + 1;
    }

    result = result > 20 ? 21 : result;

    return result;
}