#@wxy // qamwxy
#prototype.solutions
#https://discord.gg/gSSbbdBh3K

#uses python 3.12.10

import base64
import codecs
import binascii
import zlib
import re
import time
import os
import sys
import argparse
import webbrowser
import hashlib
import secrets
import struct
import hashlib
import random
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

VERSION = 1
SALT_SIZE = 16
DEK_SIZE = 32
NONCE_SIZE = 12
ARGON_ITERATIONS = 3
ARGON_MEMORY = 1 << 16
ARGON_LANES = 4
HKDF_LENGTH = 96

salo = b"vegaline_is_just_plain_simple_better"

def _derive_master_from_password(pwd: str, salt: bytes, iterations: int = ARGON_ITERATIONS,
                                 memory_cost: int = ARGON_MEMORY, lanes: int = ARGON_LANES) -> bytes:
    kdf = Argon2id(salt=salt, length=32, iterations=iterations,
                   memory_cost=memory_cost, lanes=lanes)
    return kdf.derive(pwd.encode())

def _derive_master_from_keyfile(keyfile_data: bytes) -> bytes:
    if BLAKE3_AVAILABLE:
        file_hash = blake3.blake3(keyfile_data).digest()
        return HKDF(algorithm=hashes.BLAKE2b(64), length=32, salt=None, info=b"keyfile-to-master").derive(file_hash)
    else:
        file_hash = hashlib.sha3_512(keyfile_data).digest()
        return HKDF(algorithm=hashes.SHA3_512(), length=32, salt=None, info=b"keyfile-to-master").derive(file_hash)

def _expand_keys(master: bytes) -> Tuple[bytes, bytes, bytes]:
    if BLAKE3_AVAILABLE:
        hk = HKDF(algorithm=hashes.BLAKE2b(64), length=HKDF_LENGTH, salt=None, info=b"enc-v1").derive(master)
    else:
        hk = HKDF(algorithm=hashes.SHA3_512(), length=HKDF_LENGTH, salt=None, info=b"enc-v1").derive(master)
    return hk[:32], hk[32:64], hk[64:96]

def _make_permutation(length: int, seed: bytes) -> list:
    if BLAKE3_AVAILABLE:
        seed_int = int.from_bytes(blake3.blake3(seed).digest(), "big")
    else:
        seed_int = int.from_bytes(hashlib.sha3_512(seed).digest(), "big")
    rnd = random.Random(seed_int)
    arr = list(range(length))
    for i in range(length - 1, 0, -1):
        j = rnd.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def _apply_permutation(data: bytes, perm: list) -> bytes:
    if len(perm) != len(data):
        return data
    out = bytearray(len(data))
    for i, p in enumerate(perm):
        out[i] = data[p]
    return bytes(out)

def _invert_permutation(perm: list) -> list:
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv

def _scramble(payload: bytes, key: bytes) -> bytes:
    if len(payload) == 0:
        return payload
    perm = _make_permutation(len(payload), key)
    return _apply_permutation(payload, perm)

def _unscramble(payload: bytes, key: bytes) -> bytes:
    if len(payload) == 0:
        return payload
    perm = _make_permutation(len(payload), key)
    inv = _invert_permutation(perm)
    return _apply_permutation(payload, inv)

def decrypt_with_master(master: bytes, token: str, ad: bytes = b"", seed: bytes = None) -> bytes:
    data = base64.b64decode(token)
    if seed is not None:
        scrambled = data
    else:
        seed = data[:32]
        scrambled = data[32:]
    payload = _unscramble(scrambled, seed)
    idx = 0
    version = payload[idx]
    idx += 1
    if version != VERSION:
        raise ValueError(f"unsupported version: expected {VERSION}, got {version}")
    salt = payload[idx:idx+SALT_SIZE]
    idx += SALT_SIZE
    dek_nonce = payload[idx:idx+NONCE_SIZE]
    idx += NONCE_SIZE
    dek_len = struct.unpack(">H", payload[idx:idx+2])[0]
    idx += 2
    enc_dek = payload[idx:idx+dek_len]
    idx += dek_len
    msg_nonce = payload[idx:idx+NONCE_SIZE]
    idx += NONCE_SIZE
    padding_nonce = payload[idx:idx+NONCE_SIZE]
    idx += NONCE_SIZE
    ciphertext = payload[idx:]
    kek, dek, padding_key = _expand_keys(master)
    dek = ChaCha20Poly1305(kek).decrypt(dek_nonce, enc_dek, salt + ad)
    obfuscated_text = ChaCha20Poly1305(dek).decrypt(msg_nonce, ciphertext, salt + ad)
    
    enc_padding_len = struct.unpack(">H", obfuscated_text[-20:-18])[0]
    enc_padding_info = obfuscated_text[-18:]
    padding_info = ChaCha20Poly1305(padding_key).decrypt(padding_nonce, enc_padding_info, salt + ad)
    padding_size = struct.unpack(">H", padding_info)[0]
    actual_text = obfuscated_text[padding_size:-52]
    return actual_text

def vega33(user_key, stored_hash, salt):
    rehashed_key = hashlib.sha3_512(user_key.encode('utf-8') + salt).hexdigest()
    return rehashed_key == stored_hash

def clear_terminal():
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')

time.sleep(0.15)
clear_terminal()

solutions = 'https://discord.gg/gSSbbdBh3K'
swaga = 'https://discord.gg/fRKjdGvNZK'

print(r"""
              _       _                            _      _   _
 _ __ _ _ ___| |_ ___| |_ _  _ _ __  ___   ___ ___| |_  _| |_(_)___ _ _  ___
| '_ \ '_/ _ \  _/ _ \  _| || | '_ \/ -_)_(_-</ _ \ | || |  _| / _ \ ' \(_-<
| .__/_| \___/\__\___/\__|\_, | .__/\___(_)__/\___/_|\_,_|\__|_\___/_||_/__/
|_|                       |__/|_|

""")

def rot13(s: str) -> str:
    return codecs.decode(s, 'rot_13')

def deobfuscate_main(data: str) -> str:
    vars = {k: re.search(rf"{k} = '([^']+)'", data) for k in ['morpheus', 'trinity', 'oracle', 'keymaker']}
    if not all(vars.values()):
        raise ValueError("missing vars in main_min.py")
    neo = ''.join([vars['morpheus'].group(1), rot13(vars['trinity'].group(1)),
                   vars['oracle'].group(1), rot13(vars['keymaker'].group(1))])
    return base64.b64decode(neo).decode('utf-8')

def deobfuscate_payload1(data: str) -> str:
    vars = {k: re.search(rf"{k} = '([0-9a-fA-F]+)'" if k in ['morpheus', 'oracle'] else rf"{k} = '([^']+)'", data)
            for k in ['morpheus', 'trinity', 'oracle', 'keymaker']}
    if not all(vars.values()):
        raise ValueError("missing vars in payload1")
    neo = ''.join([binascii.unhexlify(vars['morpheus'].group(1)).decode('utf-8'), rot13(vars['trinity'].group(1)),
                   binascii.unhexlify(vars['oracle'].group(1)).decode('utf-8'), rot13(vars['keymaker'].group(1))])
    return zlib.decompress(base64.b64decode(neo)).decode('utf-8')

def deobfuscate_payload2(data: str) -> str:
    vars = {k: re.search(rf"{k} = '([^']+)'", data) for k in ['morpheus', 'trinity', 'oracle', 'keymaker']}
    if not all(vars.values()):
        raise ValueError("missing vars in payload2")
    neo = ''.join([vars['morpheus'].group(1), rot13(vars['trinity'].group(1)),
                   vars['oracle'].group(1), rot13(vars['keymaker'].group(1))])
    return base64.b64decode(neo).decode('utf-8')

def deobfuscate_payload3(data: str) -> str:
    vars = {k: re.search(rf"{k} = '([0-9a-fA-F]+)'" if k in ['morpheus', 'oracle'] else rf"{k} = '([^']+)'", data)
            for k in ['morpheus', 'trinity', 'oracle', 'keymaker']}
    if not all(vars.values()):
        raise ValueError("missing vars in payload3")
    neo = ''.join([binascii.unhexlify(vars['morpheus'].group(1)).decode('utf-8'), rot13(vars['trinity'].group(1)),
                   binascii.unhexlify(vars['oracle'].group(1)).decode('utf-8'), rot13(vars['keymaker'].group(1))])
    return zlib.decompress(base64.b64decode(neo)).decode('utf-8')

def deobfuscate_payload4(data: str) -> str:
    vars = {k: re.search(rf"{k} = '([^']+)'", data) for k in ['morpheus', 'trinity', 'oracle', 'keymaker']}
    if not all(vars.values()):
        raise ValueError("missing vars in payload4")
    neo = ''.join([vars['morpheus'].group(1), rot13(vars['trinity'].group(1)),
                   vars['oracle'].group(1), rot13(vars['keymaker'].group(1))])
    return base64.b64decode(neo).decode('utf-8')

def deobfuscate_payload5(data: str) -> str:
    vars = {k: re.search(rf"{k} = '([0-9a-fA-F]+)'" if k in ['morpheus', 'oracle'] else rf"{k} = '([^']+)'", data)
            for k in ['morpheus', 'trinity', 'oracle', 'keymaker']}
    if not all(vars.values()):
        raise ValueError("missing vars in payload5")
    neo = ''.join([binascii.unhexlify(vars['morpheus'].group(1)).decode('utf-8'), rot13(vars['trinity'].group(1)),
                   binascii.unhexlify(vars['oracle'].group(1)).decode('utf-8'), rot13(vars['keymaker'].group(1))])
    return zlib.decompress(base64.b64decode(neo)).decode('utf-8')

def deobfuscate_payload6(data: str) -> str:
    vars = {k: re.search(rf"{k} = '([^']+)'", data) for k in ['morpheus', 'trinity', 'oracle', 'keymaker']}
    if not all(vars.values()):
        raise ValueError("missing vars in payload6")
    neo = ''.join([vars['morpheus'].group(1), rot13(vars['trinity'].group(1)),
                   vars['oracle'].group(1), rot13(vars['keymaker'].group(1))])
    return base64.b64decode(neo).decode('utf-8')

def deobfuscate_payload7(data: str) -> str:
    pyc = re.search(r"'pyc'\s*:\s*\"\"\"(.*?)\"\"\"", data, re.DOTALL)
    pye = re.search(r"'pye'\s*:\s*\"\"\"(.*?)\"\"\"", data, re.DOTALL)
    key = re.search(r"['\"]([lI]+)['\"]", data, re.DOTALL)
    if not all([pyc, pye, key]):
        raise ValueError("missing AES components in payload7")
    cipher = base64.b85decode((pyc.group(1) + pye.group(1)).encode('utf-8'))
    aes = AES.new(PBKDF2(key.group(1), cipher[:16], dkLen=32, count=1000000), AES.MODE_GCM, nonce=cipher[16:32])
    return aes.decrypt_and_verify(cipher[48:], cipher[32:48]).decode('utf-8')

def deobfuscate(input_file: str, target: int, inclusive: bool) -> None:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = f.read()

        current = deobfuscate_main(data)
        start = 1 if inclusive else target

        for i in range(1, target + 1):
            current = globals()[f'deobfuscate_payload{i}'](current)
            if i >= start:
                with open(f'payload{i}_decoded.py', 'w', encoding='utf-8') as f:
                    f.write(current)
                print(f"success payload{i}_decoded.py\n")

        print("quantuum base64 protection moment")
        print(solutions)

    except Exception as e:
        print(f"err: {e}")
        sys.exit(1)



def decrypt_and_validate_encrypted_strings():
    vegaline_encrypted = "w4ijPTT8sXbG4Nm10HPdKpVh4sGw8HsAixjnLXnsk8iqxOl4hhsolRE6sMohZNEntyvKn1LhMX3iKO8tdbcTAnsOV8jvIuBEN+0HBuEAMDQXl6IjH4wyMn12FcOExAu2vcY+eME4eUN0LF/hWdJc4P9aE7TyIqBFY00BfZ6sPb25BQ3Z6NAroDdDI896fwpMAH73IydPh84u8co8mIGNw8OPPbcBcAgs2PSm2MYeUsy6IzpDPjv5gPFg3IbTr+CSfovh/3Js8CtODEwkxwGqjzaH75cGSPQPVSfGS9EHVoihoZcn/aKP0FIZW4VrrT8OquWtMt72wPOHSq2Xif4HtwmHzOF8O4AfP9HRhR+9mHmrqL0fOlkpqwkM7wyoIqWzCTDwAErAUmRIBEu7KRjoeK0lOx1nEiJ1kD0PCqNIaRHEEmkWu7wDZ2zEnxVk7PgsBO5VVLIKbeC3ZY5MYQmyJRcrtc7MOmZmx9YPhu1RQzEGh4TwKeUmUJ7ow2Mbqr8RhoNWbpqkutRvdspcX/NpQL1oLXn5mvpImvz7z93Uw6gzSQdUNYX8dLorRZYrOnspn/zJT2CuJKICAa91bsSYEKH5+rkhDjvgOG4dRECUNm2EL4Jh/EHnCqqX80HeF4EI1tAmFPbO1yFZTz6sNJ6hRKXrWSWB4A=="
    evawarepasta_encrypted = "OXWhQdwSygp3/R7JQY7Wyg1m2RXYa5ARz1YmNalbr8cPGDApnF+XzOUixw5cC9hZSjJxhbFZNk6FzBh3aCxAwVaoU0UId2uHntX4SyQ4Lk7uQOEexAobOc07pNNZKvlM00TYOz4/FfJdNKIwJU8WknRQNd2/DrrpN1Y9EpKdPnkdO3V/ZoCOtbpZxu9kVreL6z8g+EkWq1J8Cp8pOlOnF5lgx7tPYmLAv0ptV0hAy6znTOsJpk/1AYpgfxjgD7Nei4mKdarWwPHaG7MroRLhIcXr1kOtfLQy4wDOQc+0OioSCFa2u1JsnN9dWRMDgpJzTfcCq+/XArA3v+xEmkPSv7U8vl6CnN7lAvexMz6wA5hHWy345KhqtfhpbA+chLaaR5wrvyvyVue6pyc0L6T6xGRVYMMXitS1LoI0PhR28XLqNpXpqg3opS34cRgITw1xfEm835s21Kd7XhgRV/wr1WnVi1mZ2arHZTC0F9HWqutAp0juCwUJIAkN1m865DMgjlpwznPrWspWsCzUcMsie3Seg7V9dZt3RPYlr2BWCpOMsLYX5BXBCCmnWHRp1M7fCMvgETqloy2m+OOAjGzxPvjR5Me/+AU9YssivbG2SlRYGaB58gKhkQ4EsGqOsp6jZ5wUBXpfJXcOaEag2oxuF2T7Rvcpv0/9H0gHUzhPTkdZ3rsAHLDACjTSPZhzAfqi/XtAw0SeQWfJAzflJnokDYV/jZeIht7RdhSiCwDAGIym6qqvY1rzrhkReb4vdvI2IIHceBFLLA=="
    
    try:
        if not os.path.exists("key.bin"):
            return False, None, None
        
        if not os.path.exists("key_scramble.json"):
            return False, None, None
        
        with open("key.bin", "rb") as f:
            keyfile_data = f.read()
        
        with open("key_scramble.json", "r") as f:
            import json
            seeds_b64 = json.load(f)
        seeds = [base64.b64decode(seed) for seed in seeds_b64]
        
        if len(seeds) != 2:
            return False, None, None
        
        master = _derive_master_from_keyfile(keyfile_data)
        decrypted_lines = []
        
        encrypted_lines = [vegaline_encrypted, evawarepasta_encrypted]
        
        for idx, encrypted_line in enumerate(encrypted_lines):
            try:
                ad = f"line_{idx}".encode()
                decrypted_data = decrypt_with_master(master, encrypted_line, ad, seeds[idx])
                decrypted_text = decrypted_data.decode('utf-8')
                decrypted_lines.append(decrypted_text)
            except Exception as e:
                return False, None, None
        
        vegaline_hash = decrypted_lines[0].strip()
        evawarepasta_hash = decrypted_lines[1].strip()
        
        return True, vegaline_hash, evawarepasta_hash
        
    except Exception as e:
        return False, None, None

if __name__ == "__main__":
    success, vegaline_hash, evawarepasta_hash = decrypt_and_validate_encrypted_strings()
    
    if not success:
        print("\nquantuum devs are not very smart, are they?")
        webbrowser.open(solutions, new=2)
        webbrowser.open(swaga, new=2)
        webbrowser.open(solutions, new=2)
        webbrowser.open(swaga, new=2)
        webbrowser.open(solutions, new=2)
        webbrowser.open(swaga, new=2)
        sys.exit()
    
    uinput = input("key: ")
    
    if vega33(uinput, vegaline_hash, salo) or vega33(uinput, evawarepasta_hash, salo) or '':
        print("\nSWAGaline js better")
    else:
        print("\nquantuum devs are not very smart, are they?")
        webbrowser.open(solutions, new=2)
        webbrowser.open(swaga, new=2)
        webbrowser.open(solutions, new=2)
        webbrowser.open(swaga, new=2)
        webbrowser.open(solutions, new=2)
        webbrowser.open(swaga, new=2)
        sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="input decrypted pyc (pyc_decrypted.py)")
    parser.add_argument("--p1", action="store_const", const=1, dest="target")
    parser.add_argument("--p2", action="store_const", const=2, dest="target")
    parser.add_argument("--p3", action="store_const", const=3, dest="target")
    parser.add_argument("--p4", action="store_const", const=4, dest="target")
    parser.add_argument("--p5", action="store_const", const=5, dest="target")
    parser.add_argument("--p6", action="store_const", const=6, dest="target")
    parser.add_argument("--p7", action="store_const", const=7, dest="target")
    parser.add_argument("--i", action="store_true", dest="inclusive")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"err: file '{args.input_file}' does not exist")
        sys.exit(1)

    target = args.target if args.target is not None else 7
    deobfuscate(args.input_file, target, args.inclusive)