union Number {
    int i;
    char c;
};

int main() {
    union Number n;
    n.missing = 5;
    return 0;
}