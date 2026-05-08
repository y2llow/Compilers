int main() {
    int x = 1;
    int result = 0;

    switch (x) {
        case 1: {
            int local = 10;
            result = local;
            break;
        }

        default: {
            int local = 20;
            result = local;
            break;
        }
    }

    return result;
}