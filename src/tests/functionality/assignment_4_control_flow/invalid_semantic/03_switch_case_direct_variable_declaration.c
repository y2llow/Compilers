int main() {
    int x = 1;

    switch (x) {
        case 1:
            int local = 10;
            x = local;
            break;

        default:
            x = 0;
            break;
    }

    return x;
}