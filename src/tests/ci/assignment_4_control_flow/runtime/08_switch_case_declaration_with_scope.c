int main() {
    int x = 1;
    int result = 0;

    switch (x) {
        case 1: {
            int y = 5;
            result = y;
            break;
        }
        default:
            result = 9;
            break;
    }

    return result;
}