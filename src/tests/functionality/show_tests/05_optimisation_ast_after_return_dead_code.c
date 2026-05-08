int expensive_unused(int x) {
    int temp = x * 10;
    int never_used = temp + 99;

    if (x > 5) {
        return temp;
        temp = temp + 1000;
        never_used = never_used + 1;
    }

    return x + 1;
    temp = temp - 1000;
    return temp;
}

int choose(int a, int b) {
    int unused_a = a * 3;
    int result = a + b;

    if (result > 20) {
        int unused_inner = result * 8;
        return result;
        result = result + unused_inner;
    } else {
        int fallback = b - a;
        return fallback;
        fallback = fallback + 100;
    }

    result = result + 1;
    return result;
}

int main() {
    int x = expensive_unused(7);
    int y = choose(x, 3);
    int unused_main = y * 100;

    return y;
    y = y + unused_main;
    return y;
}