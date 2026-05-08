int main() {
    int i = 0;
    int result = 0;

    while (i < 3) {
        int j = 0;

        for (j = 0; j < 5; j = j + 1) {
            if (j == 1) {
                continue;
            }

            if (j == 4) {
                break;
            }

            result = result + j;
        }

        i = i + 1;
    }

    return result;
}
