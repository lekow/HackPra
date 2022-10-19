#!/bin/sh

/bin/echo -n "Verifying msg1: "
openssl dgst -sha1 -verify vk.pem -signature msg1.sig msg1.txt

/bin/echo -n "Verifying msg2: "
openssl dgst -sha1 -verify vk.pem -signature msg2.sig msg2.txt

/bin/echo -n "Verifying msg3: "
openssl dgst -sha1 -verify vk.pem -signature msg3.sig msg3.txt
