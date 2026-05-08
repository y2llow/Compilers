int main() {
    int x = 1;

    {
        int x = 5;
        x = x + 1;
    }

    x = x + 2;

    return x;
}