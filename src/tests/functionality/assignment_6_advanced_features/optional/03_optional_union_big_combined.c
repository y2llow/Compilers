#include <stdio.h>

union Number {
    int i;
    char c;
    float f;
};

typedef union Number Number;

struct Pair {
    int left;
    int right;
};

union Box {
    int value;
    struct Pair pair;
    char letter;
};

struct Container {
    int id;
    union Number data;
    union Box box;
};

int main() {
    union Number n;
    union Number* p;

    Number alias_value;

    union Number arr[3];

    struct Container container;

    union Box box;

    int total;

    n.i = 5;

    p = &n;
    p->i = p->i + 2;

    alias_value.i = 11;

    arr[0].i = 3;
    arr[1].i = 4;
    arr[2].i = 5;

    container.id = 20;
    container.data.i = 6;
    container.box.value = 8;

    box.pair.left = 12;
    box.pair.right = 22;

    total = 0;

    total = total + n.i;
    total = total + alias_value.i;
    total = total + arr[0].i;
    total = total + arr[1].i;
    total = total + arr[2].i;
    total = total + container.data.i;
    total = total + container.box.value;
    total = total + box.pair.left;
    total = total + box.pair.right;

    printf("%d", total);

    return total - 56;
}