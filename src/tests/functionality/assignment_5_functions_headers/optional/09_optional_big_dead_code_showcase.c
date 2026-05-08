int helper(int x) {
    int unused_local = 123;

    if (0) {
        x = 99;
    } else {
        x = x + 1;
    }

    while (0) {
        x = 50;
    }

    for (; 0; ) {
        x = 60;
    }

    return x;

    x = 777;
}

int main() {
    int result = 0;
    int never_used = 42;

    result = helper(4);

    while (result < 10) {
        result = result + 1;
        break;
        result = 99;
    }

    int i = 0;
    while (i < 3) {
        i = i + 1;
        continue;
        result = 88;
    }

    if (0) {
        result = 100;
    } else {
        result = result + 5;
    }

    return result;
}
