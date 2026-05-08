enum Status {
    READY,
    BUSY,
    OFFLINE
};

int main() {
    int x = READY + BUSY + OFFLINE;
    return x;
}
