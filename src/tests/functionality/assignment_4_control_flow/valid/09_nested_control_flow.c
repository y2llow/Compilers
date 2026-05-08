int main() {
    int x = 0;
    int result = 0;

    while (x < 5) {
        {
            int temp = x * 2;

            if (temp > 4) {
                result = result + temp;
            } else {
                result = result + 1;
            }
        }

        x = x + 1;
    }

    return result;
}