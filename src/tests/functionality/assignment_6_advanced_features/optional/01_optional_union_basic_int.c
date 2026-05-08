union Number {
    int i;
    char c;
    float f;
};

int main() {
    union Number n;
    n.i = 5;
    return n.i;
}