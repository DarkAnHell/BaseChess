# lowercase == white, uppercase == black
# p == pawn
# n == kNight
# b == Bishop
# r == Rook
# q == Queen
# k == King
# . == empty space
BASE_CHESS_LOOKUP_TABLE = [".","p","n","b","r","q","k","P","N","B","R","Q","K"]

#message between 26 and 32 chars

# ENCODE LOGIC
def _encode_ingest(c: str, _previous_state: str = "") -> str:
    """
    Ingests a single char, + previous state
    Outputs a state to be `encode_digest`ed at the end. 
    """
    assert(len(c) == 1)
    o = ord(c.encode('ascii'))
    assert(o < 128)
    return _previous_state + bin(o)[2:].zfill(7)

def _encode_digest(final_state: str) -> str:
    """
    Digests a state computed from `encode_ingest`, outputs a chess-encoded string.
    """
    res = ""
    i = 0
    while i < len(final_state):
        jump = 4
        if i+3 >= len(final_state):
            #need to make sure up to 3 bits are used for encoding completion
            final_state += "0"*(3-(len(final_state)-i))
            res += BASE_CHESS_LOOKUP_TABLE[int(final_state[i:len(final_state)], 2)]
        else:
            index = int(final_state[i:i+4], 2)
            if index > 7 and index < len(BASE_CHESS_LOOKUP_TABLE): # if it can hold 4 bits, do it
                res += BASE_CHESS_LOOKUP_TABLE[index]
            else:
                res += BASE_CHESS_LOOKUP_TABLE[int(final_state[i:i+3], 2)]
                jump = 3
        i += jump

    # fill empty spaces in the board
    res += "."*(64-len(res))
    if len(res) > 64: raise ValueError("Message too large")
    return res

def encode_chess(s: str) -> str:
    """
    Encodes the given string into another 'chess-encoded' string.
    String length is up to 26 reliably, but may go up to 32 with good bit alignment.
    """
    state = ""
    for c in s:
        state = _encode_ingest(c, state)
    return _encode_digest(state)
# ENCODE LOGIC END

# DECODE LOGIC
def _decode_ingest(p: str, _previous_state: str = "") -> str:
    """
    Ingests a single 'piece' of chess (str), + previous state
    Outputs a state to be decoded with `decode_digests`. 
    """
    return _previous_state + bin(BASE_CHESS_LOOKUP_TABLE.index(p))[2:].zfill(3)

def _decode_digest(final_state: str) -> str:
    """
    Digests a state computed from `decode_ingest`, outputs a chess-decoded string.
    """
    res = ""
    last = 0
    for i in range(7,len(final_state), 7):
        res += chr(int(final_state[last:i], 2))
        last = i
    if last < len(final_state):
        res += chr(int(final_state[last:len(final_state)], 2))

    return res.rstrip('\x00') # Right-most NUL are just empty spaces on the board, not from the message

def decode_chess(chess: str) -> str:
    """
    Decodes a 'chess-encoded' string into the original human-readable string.
    Encoded string must be exactly 64 characters.
    """
    assert(len(chess) == 64)
    state = ""
    for piece in chess:
        state = _decode_ingest(piece, state)
    return _decode_digest(state)
# DECODE LOGIC END

# DISPLAY HELPER
def display_chess(l: str):
    i = 0
    for i, piece in enumerate(l):
        if i > 0 and i % 8 == 0:
            print()
        print(piece, end =" ")
    print()
# DISPLAY HELPER END

## DEMOS AND TESTS
# Full ASCII symbol support
assert('!"#$%&()*+,-./:;<=>?@[]^_{}|~`' == decode_chess(encode_chess('!"#$%&()*+,-./:;<=>?@[]^_{}|~`')))
# Full char support
assert('qwertyuiopasdfghjklzxcvbnm' == decode_chess(encode_chess('qwertyuiopasdfghjklzxcvbnm')))
assert('QWERTYUIOPASDFGHJKLZXCVBNM' == decode_chess(encode_chess('QWERTYUIOPASDFGHJKLZXCVBNM')))
# Full number support
assert('1234567890' == decode_chess(encode_chess('1234567890')))
# Case sensitive
assert('AAA' != decode_chess(encode_chess('aaa')))
# Full ASCII control characters support
ctrl_char = ''.join([ f"{chr(i)}" for i in range(30)]) # with control characters the limit is 30 chars.
assert(ctrl_char == decode_chess(encode_chess(ctrl_char)))
ctrl_char = ''.join([ f"{chr(i)}" for i in range(30,32)])
assert(ctrl_char == decode_chess(encode_chess(ctrl_char)))

# 32 characters with good alignment, easy to find
assert('A'*32 == decode_chess(encode_chess('A'*32)))
# 36 characters absolute MAX, but probably not useful in this state
# 32 bytes + 1 'saved bit' * 32 = 32 bytes + 4.5 bytes ~= 36 chars.

# display_chess(encode_chess("This ChA!!enge w4$ r3@| fvn 2do"))
## END DEMOS AND TESTS
