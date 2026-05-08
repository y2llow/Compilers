struct Node {
    int value;
    struct Node* next;
};

int main() {
    struct Node a;
    struct Node b;

    a.value = 3;
    b.value = 4;

    a.next = &b;

    return a.next->value;
}