#include <stdio.h>

struct Node {
    int value;
    int count;
};

int getCount(struct Node* n) {
    return n->count;
}

int main() {
    struct Node node;
    node.value = 7;
    node.count = 3;

    struct Node* ptr;
    ptr = &node;

    ptr->value = 99;
    ptr->count = 10;

    int result;
    result = getCount(ptr);

    printf("%d\n", ptr->value);
    printf("%d\n", result);

    return 0;
}