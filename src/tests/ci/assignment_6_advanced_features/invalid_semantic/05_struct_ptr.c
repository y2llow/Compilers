#include <stdio.h>

struct Node {
    int value;
    int count;
};

typedef int Node;

int main() {
    struct Node node;
    node.value = 5;

    node->value = 10;

    struct Node* ptr;
    ptr = &node;

    ptr->data = 99;

    return 0;
}