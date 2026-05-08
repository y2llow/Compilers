struct Bag {
    int values[3];
};

int main() {
    struct Bag b;

    b.values[0] = 2;
    b.values[1] = 4;
    b.values[2] = 6;

    return b.values[0] + b.values[1] + b.values[2];
}