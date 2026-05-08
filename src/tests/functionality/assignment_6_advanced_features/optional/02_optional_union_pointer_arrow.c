union Number {
    int i;
    char c;
};

int main() {
    union Number n;
    union Number* p;

    p = &n;
    p->i = 7;

    return p->i;
}