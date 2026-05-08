struct Packet {
    int length;
    int code;
};

struct Header {
    int src;
    struct Packet data;
};

int main() {
    struct Header h;

    h.data.missing = 5;

    return 0;
}