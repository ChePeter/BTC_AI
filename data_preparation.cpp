#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <openssl/bn.h>
#include <openssl/ec.h>
#include <openssl/err.h>
#include <openssl/symhacks.h>

using namespace std;

int main() {
	int bits = 256;

	unsigned char buf[32];

	char *pr;

	EC_GROUP *group;
	EC_KEY *eckey = EC_KEY_new();
	EC_POINT *P;

	BN_CTX *ctx = BN_CTX_new();
	BIGNUM *x = BN_new();
	BIGNUM *n = BN_new();  // начало последовательности точек кривой
	BIGNUM *y = BN_new();

	char e_buf[256];

	FILE * xFile;
	FILE * yFile;
	FILE * rFile;
	xFile = fopen("x600_btc_32_LH.bin", "wb");
	yFile = fopen("y600_btc_32_LH.bin", "wb");

	rFile = fopen("../PM_rand/PM_rand_600.bin", "rb");
	if (rFile==NULL)
	{ cout<<" PM_rand.bin NOT FOUND"; return -1; }

	srand(time(NULL));
// nid 714. curve secp256k1
	int nid = 714;
	if ((group = EC_GROUP_new_by_curve_name(nid)) == NULL) {
		fprintf(stdout, "\nEC_GROUP_new_curve_name() failed with"
				" curve %s\n  nid %x", nid);
	}
	if (eckey == NULL) {
		cout << "ABORT2 ";
		ERR_error_string(ERR_get_error(), e_buf);
		cout << "E_BUF " << e_buf << endl;
	}

	if (!EC_KEY_set_group(eckey, group)) {
		cout << "ABORT3 ";
		ERR_error_string(ERR_get_error(), e_buf);
		cout << "E_BUF " << e_buf << endl;
	}

	EC_GROUP_precompute_mult(group, ctx);

	P = EC_POINT_new(group);

	BN_rand(n, bits, BN_RAND_TOP_ONE, BN_RAND_BOTTOM_ANY);
	// n - начало выборки
	int NN = 60000;

	for (int i = 0; i < NN; i++) {

		if ((rand() % 128) < 16) {
			pr = (char *) "1";

			if (!EC_POINT_mul(group, P, n, NULL, NULL, ctx)) {
				cout << "ABORT_10 ";
				ERR_error_string(ERR_get_error(), e_buf);
				cout << "E_BUF " << e_buf << endl;
			}
			if (!EC_POINT_get_affine_coordinates_GFp(group, P, x, y, ctx)) {
				cout << "ABORT_11 ";
				ERR_error_string(ERR_get_error(), e_buf);
				cout << "E_BUF " << e_buf << endl;
			}
			BN_bn2bin(y, buf);
		} else {
			pr = (char *) "0";
			int cind = fread(buf, 32, 1, rFile); // read 32 byte = 256 bit
		}
		fwrite(buf, 32, 1, xFile);
		BN_add_word(n, 1L);  // in P new point n+i
		fwrite(pr, 1, 1, yFile);

	}

	fclose(xFile);
	fclose (yFile);

	BN_CTX_free(ctx);
	EC_GROUP_free(group);
	BN_free(x);
	BN_free(y);

}
