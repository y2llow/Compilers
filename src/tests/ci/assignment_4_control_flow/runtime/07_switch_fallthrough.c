int main() {
    int x = 1;
    int result = 0;

    switch (x) {
        case 1:
            result = result + 10;
        case 2:
            result = result + 20;
            break;
        default:
            result = result + 100;
    }

    return result;
}