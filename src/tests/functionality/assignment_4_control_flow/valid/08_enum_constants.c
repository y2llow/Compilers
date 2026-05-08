enum Status {
    READY,
    BUSY,
    OFFLINE
};

int main() {
    enum Status status = BUSY;
    int x = READY + BUSY + OFFLINE;

    if (status == BUSY) {
        x = x + 10;
    }

    return x;
}