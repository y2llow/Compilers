#include <stdio.h>

struct Node {
    int value;
    struct Node* next;
};

int main() {
    struct Node n;
    n.value = 42;
    n.next = 0;
    printf("%d\n", n.value);
    return 0;
}