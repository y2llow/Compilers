enum Status {
    READY,
    BUSY,
    OFFLINE
};

int main() {
    enum Status status = OFFLINE;
    int result = 0;

    switch (status) {
        case READY:
            result = 1;
            break;

        case BUSY:
            result = 2;
            break;

        case OFFLINE:
            result = 3;
            break;

        default:
            result = 4;
            break;
    }

    return result;
}