# BaseChess

This is my entry for the Stackoverflow Coding Challenge #2, 2025 (see: https://stackoverflow.com/beta/challenges/79651567/code-challenge-2-secret-messages-in-game-boards).

## Cracking Challenge

First of all, for those here to crack the ciphers, here you have a chess board containing a secret message. Have fun:

```none
R B R p R b K k 
N p . b k N N p 
n . R . P p b Q 
Q p P B n N p k 
P b n p p . N p 
K B B K . b P . 
N p B Q Q b b B 
. . K Q p p Q k
```

### Hints for cracking

>! 1 - The hidden message is in English (but l33t coded somewhat)

>! 2 - The cipher is read left to right, up to down.

>! 3 - Think in binary

## Cipher explanation

*BaseChess* translates arbitrary text (see below) into a (very probably game-invalid) chess board state. **It can fit \~30 characters reliably in one board** (see below).

I set out to build something that:

- Used chess. Because I like it.

- Is less than 100 lines long. Because I'm horrible with feature creep.

- Could be feasibly done by a human. Not a competition requirement, but i wanted to anyways.

- Is versatile enough to fit almost any (short) English message.

- Is as space efficient as possible. I paid for 64 squares and I'm going to use them!

- Used no libraries.

### Examples

First, some examples:

Symbol meanings:

```
# lowercase == white, uppercase == black
# p == Pawn
# n == kNight
# b == Bishop
# r == Rook
# q == Queen
# k == King
# . == empty space
```

```none
One line: BQPpn.bpbQQRbBbKR.bnbKkNpkBRpBnNpNQpbKPkNQ.NpQQbkNpNQnbNbKk.....

Chess mode:
B Q P p n . b p 
b Q Q R b B b K 
R . b n b K k N 
p k B R p B n N 
p N Q p b K P k 
N Q . N p Q Q b 
k N p N Q n b N 
b K k . . . . . 
```

Reads: "My entry is the best, no bias"

```none
One line: NpKbKbkPPBbppRbQQpkNpkBQkNpNbQpQ.NpRPQQbPkPkPp.pQpNbkPPpR.bbPBr.

Chess mode:
N p K b K b k P 
P B b p p R b Q 
Q p k N p k B Q 
k N p N b Q p Q 
. N p R P Q Q b 
P k P k P p . p 
Q p N b k P P p 
R . b b P B r . 
```

Reads: "According to all known laws of"

```none

One line: n.Rpp.kB.BnBBn.RnRBnkQ.QnQBbkPnbQbKbkQPpPP..QbQQbkQPPQPkPPpPkK..

Chess mode:
n . R p p . k B 
. B n B B n . R 
n R B n k Q . Q 
n Q B b k P n b 
Q b K b k Q P p 
P P . . Q b Q Q 
b k Q P P Q P k 
P P p P k K . . 
```

Reads: !"#$%&()\*+,-./:;\<=\>?@\[\]^\_{}|\~\`

### Features

- **Accepts any (non-extended) [ASCII](https://www.ascii-code.com/) character, including control characters** (so, from 0 to 127).

```python
# Full ASCII symbol support
assert('!"#$%&()*+,-./:;<=>?@[]^_{}|~`' == decode_chess(encode_chess('!"#$%&()*+,-./:;<=>?@[]^_{}|~`')))
# Full char support
assert('qwertyuiopasdfghjklzxcvbnm' == decode_chess(encode_chess('qwertyuiopasdfghjklzxcvbnm')))
assert('QWERTYUIOPASDFGHJKLZXCVBNM' == decode_chess(encode_chess('QWERTYUIOPASDFGHJKLZXCVBNM')))
# Full number support
assert('1234567890' == decode_chess(encode_chess('1234567890')))
# Full ASCII control characters support
ctrl_char = ''.join([ f"{chr(i)}" for i in range(30)]) # with control characters the limit is 30 chars.
assert(ctrl_char == decode_chess(encode_chess(ctrl_char)))
ctrl_char = ''.join([ f"{chr(i)}" for i in range(30,32)])
assert(ctrl_char == decode_chess(encode_chess(ctrl_char)))
```

- Is **case sensitive.**

```python
assert('AAA' != decode_chess(encode_chess('aaa')))
```

- Maximum length of the message encoded can be **realistically** **up to \~30 characters** (see below on 'how it works' for an explanation). Strict limits are:
  - 26 characters in worst case scenario.
  - \~30 characters reliably.
  - **36 characters are the technical maximum**, but honestly wont happen with any useful message.
- Could be translated by pen and paper with relatively small effort.
- Configurable look up table for extra variations against prying eyes.
- No libraries needed, just pure Python 3.

## Restrictions

- **Output text is exactly one chess board** (64 pieces/spaces). There is no technical reason for this limit, the cipher could happily continue to more 'consecutive' boards, but it was limited to follow the spirit of the challenge.

- Extended ascii characters, or other **unicode characters, are not supported**.

- It's **hard to predict the actual limit of characters** for the input before the fact, which makes it somewhat user unfriendly for strings reaching the upper limit.

- Probably something else I'm missing at the moment.

## How it works

*BaseChess* is a streaming cipher, that uses a look up table of 13 elements (1 empty space, 6 distinct white chess pieces, 6 distinct chess black pieces) to encode any given byte.

As seen below, a key feature of the cipher is the '**optimization' of a byte into 7 bits**, and the **dynamic usage of a piece to cover either 4 or 3 contiguous bits**, even from different characters.

Without these improvements, one would need 3 pieces (4,4,2 bits) to encode a single byte, leaving a theoretical maximum of 64/3 = 21 characters . But with the improvements, the cipher needs as little as 2 pieces (4,3 bits), or 3 pieces but sharing space with the next character (3,3,1 + 2 bits from next). **This allows a theoretical maximum of 64/2 = 32 characters using 4+3 bit pieces**, and potentially using 4+3(+1 from the next) bits = **36 characters**. Though admittedly, reaching this upper limit of 36 is not viable for arbitrary messages.

**Look up table**:

This table can be switched around to create your own permutation of the cipher. Shown below is the one i picked, that seemed the most logical to show case it.

```python
# lowercase == white, uppercase == black
# p == pawn
# n == kNight
# b == Bishop
# r == Rook
# q == Queen
# k == King
# . == empty space
BASE_CHESS_LOOKUP_TABLE = [".","p","n","b","r","q","k","P","N","B","R","Q","K"]
```

**Encoding**:

```pseudocode
0. Start an empty 'stream' state and an empty result string.
1. For each character in the string:
    1.1. Transform to binary
    1.2. Remove the left-most bit
    1.3. Append the resulting binary to the 'stream'
2. Iterate over the binary 'stream':
    2.1 If the next 4 bit sequence is a decimal number between 8 and 12:
        2.1.1 Take the 4 bit into an integer, use this integer in the look up table, add the found piece to the resulting cipher
    2.2 If not, do 2.1.1 but with 3 bits only.
    2.3 Advance in the stream by the amount of bits read (4 or 3)
    2.4 Repeat until stream is empty. Pad the last piece with zeros to reach 3 bits, if necessary.
```

- Step 1.2 is there because all non-extended ascii characters can be represented with 7 bits (they are \< 128). Skipping this bit allows us to gain 1 bit every 2 spaces -\> 32 bits -\> 4 extra characters for free.

- Step 2.1 is there to take advantage of the fact that we can, in some cases, store 4 bits per piece. This is only possible on the higher pieces, because for smaller values at the time of decoding there is no way of knowing if it was 4 or 3 bit (e.g. 111 vs 0111). On the other hand, always using 4 bit is not possible, since the lookup table only has 13 values, which do not cover the whole 4 bit range. (e.g. 1110 is not a possible value)

**Decoding**:

```
0. Start an empty 'stream' state and an empty result string.
1. For each 'chess piece' received:
    1.1 Look up the position in the table.
    1.2 Add the index found, in binary form (pad with 0s to 3 bits), to the stream.
2. Read the stream in jumps of 7 bits. For each 7 bit:
    2.1 Read the 7 bit string as the ascii character (binary -> dec -> ascii)
3. Remove right-most NULLs
```

- Step 3 is there to remove the left over 'padding' to always have 64 places.

## How to run it

In Python 3, once you copy paste or import it, simply:

```python
# To encode, simply call `encode_chess`
>>> encode_chess("This is a test for stackoverflow")
'RBRpRbKkNpRbKkNpNnNpkBBbKPkNNpBQbPKB.pKPkBNbNPRPQPkkKQKQpQbpQPkP'
```

```
# To decode, simply call `decode_chess`
>>> decode_chess("RBRpRbKkNpRbKkNpNnNpkBBbKPkNNpBQbPKB.pKPkBNbNPRPQPkkKQKQpQbpQPkP")
'This is a test for stackoverflow'
```

Although you probably want to display it in a fancy way once encoded. You can use this simple helper:

```
def display_chess(l: str):
    i = 0
    for i, piece in enumerate(l):
        if i > 0 and i % 8 == 0:
            print()
        print(piece, end =" ")
    print()
```

And then simply do something like:

```python
# Passing the coded string
>>> display_chess("RBRpRbKkNpRbKkNpNnNpkBBbKPkNNpBQbPKB.pKPkBNbNPRPQPkkKQKQpQbpQPkP")
R B R p R b K k 
N p R b K k N p 
N n N p k B B b 
K P k N N p B Q 
b P K B . p K P 
k B N b N P R P 
Q P k k K Q K Q 
p Q b p Q P k P 

# or feed it directly
>>> display_chess(encode_chess("This is a test for stackoverflow"))
R B R p R b K k 
N p R b K k N p 
N n N p k B B b 
K P k N N p B Q 
b P K B . p K P 
k B N b N P R P 
Q P k k K Q K Q 
p Q b p Q P k P 
```

## AI & other help disclosure

- Absolutely no AI was used in the making of this code.

- Stackoverflow was used to remind myself of python syntax.

- A rubber ducky was needed once or twice.