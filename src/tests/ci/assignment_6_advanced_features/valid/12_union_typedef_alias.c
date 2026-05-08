union Value {
    int i;
    char c;
    float f;
};

typedef union Value Value;

int main() {
    Value v;
    v.i = 9;
    return v.i;
}