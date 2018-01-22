import re
import pdb
import sys
from operator import itemgetter


class CIGAR:

    @classmethod
    def fromString(cls, string):
        """Parse a string containing a CIGAR string. Converts it into a suitable 
        format for the other functions of this module
        >>> CIGAR.fromString("5M20I2M5D").toList()
        [(5, 'M'), (20, 'I'), (2, 'M'), (5, 'D')]

        >>> CIGAR.fromString("*").toList()
        ['*']

        >>> CIGAR.fromString("").toList()
        []

        >>> CIGAR.fromString("4F")
        Traceback (most recent call last):
        ...
        ValueError: Invalid CIGAR string: "4F"
        """
        # From SAM specification v1.5, slightly adapted for single-token parsing
        pattern = r"^[0-9]+[MIDNSHPX=]" 
        string = string.strip()
        if string == '*':
            return CIGAR.fromList(['*'])
        parsed = []
        s = string
        # Parse string token (e.g. 14M) by token, re.findall is not enough,
        # because non-matching subsequences between (e.g. "14Mblabla3D4M") would
        # go unnoticed! Also it would be good to abort as early as possible if
        # an invalid string is found to avoid parsing possibly very long strings
        while s != '':
            r = re.match(pattern, s)
            if not r:
                raise ValueError('Invalid CIGAR string: "'+string+'"')
            g = r.group(0)
            parsed.append(g)
            s = s[len(g):]
            
        parsed = [(int(p[:-1]), p[-1:]) for p in parsed]

        return CIGAR.fromList(parsed)

    @classmethod
    def fromList(cls, list):
        """
        >>> str(CIGAR.fromList([(4,'M')]))
        '4M'
        >>> str(CIGAR.fromList([(4,'M'),(3,'I')]))
        '4M3I'
        >>> str(CIGAR.fromList([(3,'M'),(3,'M')]))
        '6M'
        """
        obj = CIGAR()
        if list == ['*']:
            obj._tokens = '*'
        else:
            if not all(  type(e)    == tuple      
                     and len(e)     == 2          
                     and type(e[0]) == int        
                     and e[0]       >= 1        
                     and type(e[1]) == str        
                     and len(e[1])  == 1        
                     and e[1]       in 'MIDNSHPX=' for e in list):
                raise ValueError('Invalid list to form CIGAR string')

            obj._tokens = list
        obj._changed = True
        obj.compact()
        return obj

    def toList(self):
        if self._tokens == '*':
            return ['*']
        else:
            return self._tokens

    def __str__(self):
        """
        Convert a CIGAR string object 
        >>> str(CIGAR.fromList([(3,'I'),(14,'M')]))
        '3I14M'
        >>> str(CIGAR.fromString('*'))
        '*'
        """
        if self._tokens == '*' or self._tokens == '':
            return self._tokens
        self.compact()
        return "".join(str(s[0])+s[1] for s in self._tokens)

    def compact(self):
        """Join duplicate tokens together. This is done automatically before
        printing and does not need to be explicitly called in normal operation
        >>> c = CIGAR.fromList([])
        >>> c._tokens = [(2,'M'),(3,'I'),(4,'M'),(3,'M')]
        >>> c.compact()
        >>> c._tokens
        [(2, 'M'), (3, 'I'), (7, 'M')]
        >>> c = CIGAR.fromList([])
        >>> c._tokens = [(3,'M'),(3,'I'),(3,'D'),(3,'I'),(3,'M'),(3,'I'),(3,'D')]
        >>> c.compact()
        >>> c._tokens
        [(3, 'M'), (3, 'D'), (6, 'I'), (3, 'M'), (3, 'D'), (3, 'I')]
        """
        if self._changed == False:
            return
        t = self._tokens

        if t in [[], '*']:
            return 

        # Tokens which can be reordered and joined if juxtapoxed.
        # E.g. 3I3D3I --> 3D6I
        freeToks = ['I','D']
        iFirstFree = None
        for i in range(0,len(t)):
            # ...and i != len(t)-1 makes sure that sorting (`else`-Block) takes
            # place if the token list ends with a free (=reorderable) token
            if t[i][1] in freeToks and i != len(t)-1:
                if iFirstFree == None: 
                    iFirstFree = i
            else:
                if iFirstFree != None:
                    # Sort by key
                    t[iFirstFree:i+1] = sorted(t[iFirstFree:i+1], key=itemgetter(1))
                    iFirstFree = None

        out = [t[0]]
        for i in range(1,len(t)):
            if t[i][1] == out[-1][1]:
                out[-1] = (out[-1][0] + t[i][0], t[i][1])
            else:
                out.append(t[i])


        self._tokens = out
        self._changed = False

    def operationAt(self, op, n, at):
        """Change this CIGAR string, starting at base `at` (integer) by 
        inserting one of the following operations `op` (string):
        * M: Change `n` bases
        * I: Insert `n` bases
        * D: Delete `n` bases

        >>> c = CIGAR.fromString("6M")
        >>> c.operationAt('D', 3, 2)
        >>> str(c)
        '2M3D1M'
        >>> c = CIGAR.fromString("6M3I6M")
        >>> c.operationAt('I', 3, 8)
        >>> str(c)
        '6M6I6M'
        >>> c = CIGAR.fromString("3M3I3M")
        >>> c.operationAt('D', 3, 8)
        Traceback (most recent call last):
        ...
        ValueError: The operation (3, 'D') at 8bp exceeds the end of the string (and is no insert)
        >>> c = CIGAR.fromString("6M3I6M")
        >>> c.operationAt('D', 4, 4)
        >>> str(c)
        '4M2D1I6M'
        >>> c = CIGAR.fromString("6M3I6M")
        >>> c.operationAt('D', 3, 6)
        >>> str(c)
        '12M'
        >>> c = CIGAR.fromString("1M1D1M1I1M1D")
        >>> c.operationAt('D', 3, 0)
        >>> str(c)
        '3D1M1D'
        """
        self._changed = True

        bpTokenStart = 0 # in bp (base pairs)
        # iToken and tokenLength are used ouside of loop
        for iStartToken,tokenLength in enumerate(t[0] for t in self._tokens):
            if bpTokenStart + tokenLength > at: break
            bpTokenStart += tokenLength
        rem = (n, op)
        opAt = at - bpTokenStart

        out = self._tokens[0:iStartToken]
        for i in range(iStartToken, len(self._tokens)):
            t, rem = CIGAR._mutateToken(self._tokens[i], opAt, rem)
            # Replace the current token with the output t
            out.extend(t)
            if rem == (): 
                # We're done applying the operation to the CIGAR string
                out.extend(self._tokens[i+1:])
                break
            else: 
                # Apply remaining operation at start of next token
                opAt = 0 

        # If an operation remains after all tokens have been dealt with
        if rem != (): 
            if(rem[1] == 'I'):
                out.append(rem)
            else:
                raise ValueError(("The operation {} at {}bp "
                    +"exceeds the end of the string (and is no insert)")
                    .format((n, op), at))
        self._tokens = out


    @staticmethod
    def _mutateToken(t1, p, t2):
        """Changes the token t1 by an operation t2. Both t1 and t2 are of the
        format (N, X) where N is an integer and X is a one-char string out
        of "MIDNSHPX=". Its meaning is that of a CIGAR string 'NX'
        p is an integer giving the position (relative to t1) where to change
        the CIGAR string t1 by the operation t2.

        The function returns a tuple, where the first element is a list of
        tuples which replace t1 and which, concatenated, give the new CIGAR
        string after the change. The second element is an operation t2' which
        must be applied to the token following t1 by the function which called
        this function. 

        >>> c = CIGAR() # use from...-Methods for production use!
        >>> # --- Insertions -------------------------------------------------
        >>> # Inserting into a sequence of (mis-) matches splits that sequence
        >>> c._mutateToken((5, 'M'), 2, (3, 'I'))
        ([(2, 'M'), (3, 'I'), (3, 'M')], ())
        >>> # Inserting at position 0 inserts before t1
        >>> c._mutateToken((5, 'M'), 0, (3, 'I'))
        ([(3, 'I'), (5, 'M')], ())
        >>> # Inserting after an insertion elongates that insertion
        >>> c._mutateToken((5, 'I'), 2, (3, 'I'))
        ([(8, 'I')], ())

        >>> # --- Deletions --------------------------------------------------
        >>> c._mutateToken((5, 'M'), 2, (3, 'D'))
        ([(2, 'M'), (3, 'D')], ())
        >>> # Deletion longer than the token
        >>> c._mutateToken((5, 'M'), 2, (5, 'D'))
        ([(2, 'M'), (3, 'D')], (2, 'D'))
        >>> # Deleting after a deletion deletes after that deletion 
        >>> # (removing duplicate delete tokens are removed by compact())
        >>> c._mutateToken((5, 'D'), 2, (2, 'D'))
        ([(5, 'D')], (2, 'D'))
        >>> # Deleting in an insertion shortens that insertion
        >>> c._mutateToken((4, 'I'), 2, (2, 'D'))
        ([(2, 'I')], ())

        >>> # --- Base exchanges ---------------------------------------------
        >>> # Base exchange does not change alignment
        >>> c._mutateToken((5, 'M'), 2, (1, 'M'))
        ([(5, 'M')], ())
        >>> # Base exchange does not change insertion
        >>> c._mutateToken((5, 'I'), 2, (2, 'M'))
        ([(5, 'I')], ())
        >>> # Base exchange happens after a deletion
        >>> c._mutateToken((5, 'D'), 2, (2, 'M'))
        ([(5, 'D')], (2, 'M'))
        >>> # Base exchange longer than the token
        >>> c._mutateToken((5, 'M'), 2, (5, 'M'))
        ([(5, 'M')], (2, 'M'))
        >>> # Without the reference sequence no statement can be made
        >>> # whether a base exchange introduces a point mutation or
        >>> # reverts a mutation. Therefore, all base exchanges insert
        >>> # 'M' (unspecified if match or mismatch) and never '=' (match)
        >>> # or 'X' (mismatch)
        >>> c._mutateToken((5, '='), 2, (1, 'M'))
        ([(2, '='), (1, 'M'), (2, '=')], ())
        >>> c._mutateToken((5, 'X'), 2, (1, 'M'))
        ([(2, 'X'), (1, 'M'), (2, 'X')], ())

        >>> # --- p is the 0-based base before which the operation t2 starts -
        >>> c._mutateToken((5, 'M'), 0, (2, 'D'))
        ([(2, 'D'), (3, 'M')], ())

        >>> # --- 0-length operation t2 returns t1 unchanged -----------------
        >>> c._mutateToken((5, 'D'), 2, (0, 'I'))
        ([(5, 'D')], ())
        """
        if not isinstance(p, int): 
            raise ValueError("p must be integer")
        if(p < 0): 
            raise ValueError("p may not be smaller than 0")
        if(p > t1[0]-1): 
            raise ValueError("p may not be larger than t1 length - 1")

        x1 = t1[1] # Type of changed token
        l1 = t1[0] # Length of changed token
        x2 = t2[1] # Type of change
        l2 = t2[0] # Length of change
        q  = l1 - p 

        if l2 < 0: 
            raise ValueError("length of t2 cannot be negative")
        if x1 in ['S','H'] or x2 in ['S', 'H']:
            raise ValueError("CIGAR tokens S (soft-clip) or H (hard-clip) "+
                "are not supported!")
        if x1 in ['P', 'N'] or x2 in ['P', 'N']:
            raise ValueError("CIGAR tokens P (reference padding) or "+
                    "N (skip reference) are not supported!")

        # Example: Insertion in MMM 
        # x1 = M, l1 = 12, x2 = I, l2 = 2
        # p = 5 => q = 7
        #     MMMMMMMMMMMM
        #     └─p─┘└──q──┘  p + q = l1
        # -> MMMMMIIMMMMMMM

        # --- Library of different possible function return values
        # These functions use the variables p, q, l1, l2, x1 and x2.

        #   (######, 3, ++++) ->  (##+++,+) (replace per-character)
        replaceT1 = lambda: ( [ (max(0, p   ), x1)
                              , (min(q, l2  ), x2 ) 
                              , (max(0, q-l2), x1) ]
                            , (max(0, l2-q), x2) )
        #   (######, 3, ++++) ->  (######,+) 
        absorbT2  = lambda:   ( [t1], (max(0, l2-q), x2) )
        #   (######, 3, ++++) ->  (###++++###, ) 
        insertT2  = lambda: ( [ (max(0, p), x1)
                              , t2
                              , (max(0, q), x1)]
                            , ())
        #   (######, 3, ++++) ->  (###, +) 
        shortenT1 = lambda: ( [(p + max(0, q-l2), x1)]
                            , (max(0, l2-q), x2))
        #   (######, 3, ++++) ->  (##########, ) 
        elongateT1 = lambda: ( [(l1 + l2, x1)], ())
        #   (######, 3, ++++) ->  (######, ++++) 
        postponeT2 = lambda: ( [t1], t2 )

        res = None
        # Zero-length action
        if l2 == 0: 
           res = ([t1],())
        # --- Mutate... ------------------------------------------------
        elif x2 == 'M': # 1-to-1 base change
            # Remaining length of the change if this token is done
            if x1 in ['M', 'I']:
                res = absorbT2()
            elif x1 == 'D':
                res = postponeT2()
            elif x1 in ['=', 'X']:
                res = replaceT1()
        # --- Insert... ------------------------------------------------
        elif x2 == 'I':
            if x1 in ['M', '=', 'X']:
                res = insertT2()
            elif x1 == 'I':
                res = elongateT1()
            elif x1 == 'D':
                res = shortenT1()
        # --- Delete... ------------------------------------------------
        elif x2 == 'D':
            if x1 in ['M', '=', 'X']:
                res = replaceT1()
            elif x1 == 'D':
                res = postponeT2()
            elif x1 == 'I':
                res = shortenT1()

        assert res != None

        filterZeroTokens = lambda r: \
           ( [ t for t in r[0] if t[0] > 0 ] 
           , r[1] if len(r[1]) > 0 and r[1][0] > 0 else ()     
           )
        return filterZeroTokens(res)
            





            
