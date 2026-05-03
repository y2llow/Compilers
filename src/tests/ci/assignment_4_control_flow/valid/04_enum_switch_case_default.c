enum Color { RED, GREEN, BLUE };

int main() {
    enum Color c = GREEN;
    switch (c) {
        case RED:
            return 1;
        case GREEN:
            return 2;
        default:
            return 0;
    }
}