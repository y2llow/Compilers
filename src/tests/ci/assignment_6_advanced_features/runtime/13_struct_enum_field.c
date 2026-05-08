enum Kind {
    SMALL = 2,
    LARGE = 5
};

struct Item {
    enum Kind kind;
    int value;
};

int main() {
    struct Item item;

    item.kind = LARGE;
    item.value = 3;

    return item.kind + item.value; // 5 + 3 = 8
}