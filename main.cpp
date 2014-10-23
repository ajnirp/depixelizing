#include <iostream>
#include <vector>
#include <list>
#include <set>
#include <tuple>
#include <utility>

#include <cstdlib>
#include <cassert>
#include <cmath>

#include "lodepng.h"

typedef unsigned char uchar;
typedef unsigned int uint;

#define rgb_triple tuple<uchar, uchar, uchar>
#define yuv_triple tuple<float, float, float>

using namespace std;

struct Image
{
    vector<uchar> data;
    uint width, height;
    const char* name;
    Image(const char* name) {
        this->name = name;
    }
};

struct Node {
    Image* image;
    int x, y;
    rgb_triple rgb;
    set<Node*> neighbours;
    list<pair<float, float> > vor_pts;

    Node(Image* image, int x, int y, rgb_triple rgb) {
        this->image = image;
        this->x = x;
        this->y = y;
        this->rgb = rgb;
    }

    void make_conn(Node* n) {
        if (n == nullptr)
            return;
        this->neighbours.insert(n);
        n->neighbours.insert(this);
    }

    void remove_conn(Node* n) {
        if (n == nullptr)
            return;
        this->neighbours.erase(n);
        n->neighbours.erase(this);
    }
};

rgb_triple get_rgb(Image& im, uint x, uint y) {
    uint offset = (y * im.width + x) << 2;
    return rgb_triple(im.data[offset], im.data[offset+1], im.data[offset+2]);
}

void decode_image(Image& im) {
    uint error = lodepng::decode(im.data, im.width, im.height, im.name);
    if (error) {
        cerr << "decoder error " << error << endl;
        exit(1);
    }
}

Node* get_node(Image& im, uint x, uint y, vector<Node*>& nodes) {
    if (x < 0 or y < 0 or x >= im.width or y >= im.height)
        return nullptr;
    return nodes[x + y * im.width];
}

void test_node_corresponds_to_image(Image& im, vector<Node*>& nodes) {
    for (int x = 0 ; x < im.width ; x++) {
        for (int y = 0 ; y < im.height ; y++) {
            assert(get_rgb(im, x, y) == get_node(im, x, y, nodes)->rgb);
        }
    }
}

void test_neighbours_are_mutual(Image& im, vector<Node*>& nodes) {
    for (int x = 0 ; x < im.width ; x++) {
        for (int y = 0 ; y < im.height ; y++) {
            Node* n = get_node(im, x, y, nodes);
            for (Node* ne : n->neighbours) {
                assert(ne->neighbours.find(n) != ne->neighbours.end());
            }
        }
    }
}

void test_number_of_neighbours_is_correct(Image& im, vector<Node*>& nodes) {
    uint w = im.width, h = im.height;

    // corner nodes have 3 neighbours
    assert(get_node(im, 0,   0,   nodes)->neighbours.size() == 3);
    assert(get_node(im, w-1, 0,   nodes)->neighbours.size() == 3);
    assert(get_node(im, 0,   h-1, nodes)->neighbours.size() == 3);
    assert(get_node(im, w-1, h-1, nodes)->neighbours.size() == 3);

    // border nodes have 5 neighbours
    for (int x = 1 ; x < w-1 ; x++) {
        assert(get_node(im, x, 0,   nodes)->neighbours.size() == 5);
        assert(get_node(im, x, h-1, nodes)->neighbours.size() == 5);
    }
    for (int y = 1 ; y < h-1 ; y++) {
        assert(get_node(im, 0,   y, nodes)->neighbours.size() == 5);
        assert(get_node(im, w-1, y, nodes)->neighbours.size() == 5);
    }

    // interior nodes have 8 neighbours
    for (int x = 1 ; x < w-1 ; x++) {
        for (int y = 1 ; y < h-1 ; y++) {
            assert(get_node(im, x, y, nodes)->neighbours.size() == 8);
        }
    }
}

yuv_triple rgb2yuv(rgb_triple rgb) {
    float r = get<0>(rgb) / 255.0;
    float g = get<1>(rgb) / 255.0;
    float b = get<2>(rgb) / 255.0;

    float y = (0.299 * r) + (0.587 * g) + (0.114 * b);
    float u = 0.492 * (b - y);
    float v = 0.877 * (r - y);

    return yuv_triple(y, u, v);
}

bool pixels_are_dissimilar(rgb_triple rgb1, rgb_triple rgb2) {
    yuv_triple yuv1 = rgb2yuv(rgb1);
    yuv_triple yuv2 = rgb2yuv(rgb2);

    // tuple unpacking
    float y1, u1, v1, y2, u2, v2;
    tie (y1, u1, v1) = yuv1;
    tie (y2, u2, v2) = yuv2;

    bool ydiff = abs(y1 - y2) > 48.0/255;
    bool udiff = abs(u1 - u2) > 7.0/255;
    bool vdiff = abs(v1 - v2) > 6.0/255;

    return ydiff || udiff || vdiff;
}

int main()
{
    Image im("img/smw_boo.png");
    decode_image(im);
    
    vector<Node*> nodes;

    // create nodes
    for (uint row = 0 ; row < im.height ; row++) {
        for (uint col = 0 ; col < im.width ; col++) {
            Node* n = new Node(&im, col, row, get_rgb(im, col, row));
            nodes.push_back(n);
        }
    }

    test_node_corresponds_to_image(im, nodes);

    // initialize similarity graph
    for (uint row = 0 ; row < im.height ; row++) {
        for (uint col = 0 ; col < im.width ; col++) {
            Node* n = get_node(im, col, row, nodes);
            for (int x = -1 ; x <= 1 ; x++) {
                for (int y = -1 ; y <= 1 ; y++) {
                    if (x != 0 or y != 0) {
                        Node* neighbour = get_node(im, col+x, row+y, nodes);
                        n->make_conn(neighbour);
                    }
                }
            }
        }
    }

    test_neighbours_are_mutual(im, nodes);
    test_number_of_neighbours_is_correct(im, nodes);

    // remove dissimilar edges by yuv metric
    for (int x = 0 ; x < im.width ; x++) {
        for (int y = 0 ; y < im.height ; y++) {
            Node* n = get_node(im, x, y, nodes);
            list<Node*> neighbours_to_remove;
            for (Node* ne : n->neighbours) {
                if (pixels_are_dissimilar(n->rgb, ne->rgb)) {
                    neighbours_to_remove.push_back(ne);
                }
            }
            for (Node* ne : neighbours_to_remove) {
                n->remove_conn(ne);
            }
        }
    }

    return 0;
}