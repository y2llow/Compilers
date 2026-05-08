/*
 * AST visualizer showcase
 * This file is meant to create a rich AST graph.
 */

#define LIMIT 5
#define TRUE 1
#define FALSE 0

typedef int MyInt;

enum Mode {
    MODE_ADD = 1,
    MODE_SUB = 2
};

struct Point {
    int x;
    int y;
};

int add(int a, int b);
int multiply(int a, int b);
int compute(struct Point* p, int mode);

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

int compute(struct Point* p, int mode) {
    int value = 0;

    if (mode == MODE_ADD) {
        value = p->x + p->y;
    } else {
        value = p->x - p->y;
    }

    return value;
}

int main() {
    MyInt numbers[3] = {1, 2, 3};
    struct Point point;

    int i = 0;
    int total = 0;
    int flag = TRUE;
    int result = 0;

    point.x = 4;
    point.y = 2;

    for (i = 0; i < 3; i = i + 1) {
        total = total + numbers[i];
    }

    if (flag && total > 0) {
        result = compute(&point, MODE_ADD);
    } else {
        result = compute(&point, MODE_SUB);
    }

    switch (result) {
        case 6:
            result = multiply(result, 2);
            break;

        case 2:
            result = add(result, 10);
            break;

        default:
            result = 1;
            break;
    }

    result = result > 10 ? result : 10;

    result = result + sizeof(int);
    result = result + (int) 3.14;

    return result;
}