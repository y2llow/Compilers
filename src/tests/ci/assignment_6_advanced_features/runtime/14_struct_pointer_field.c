struct Node {
    int value;
    struct Node* next;
};

int main() {
    struct Node a;
    struct Node b;

    a.value = 4;
    b.value = 9;

    a.next = &b;

    return a.next->value;
}