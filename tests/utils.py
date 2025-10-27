from dataclasses import field

from pydantic import BaseModel

class PointCounter():
    def __init__(self, start=0):
        self._setup(start)
    
    def _setup(self, start=0):
        self._counter = start
    
    def reset(self, start=0) -> int:
        self._setup(start)
        return self._counter

    def next(self) -> int:
        self._counter += 1
        return self._counter

    def __hash__(self):
        return hash(self._counter)
    
    def __eq__(self, value):
        return self._counter == value

    def __str__(self):
        return str(self._counter)

class BlastResult(BaseModel):
    fields_used: set[str] = field(default_factory=set)
    qseqid: str=None
    qgi: str=None
    qacc: str=None
    qaccver: str=None
    qlen: int=None
    sseqid: str=None
    sallseqid: str=None
    sgi: str=None
    sallgi: str=None
    sacc: str=None
    saccver: str=None
    sallacc: str=None
    slen: int=None
    qstart: int=None
    qend: int=None
    sstart: int=None
    send: int=None
    qseq: str=None
    sseq: str=None
    evalue: float=None
    bitscore: float=None
    score: int=None
    length: int=None
    pident: float=None
    nident: int=None
    mismatch: int=None
    positive: int=None
    gapopen: int=None
    gaps: int=None
    ppos: float=None
    frames: str=None
    qframe: str=None
    sframe: str=None
    btop: str=None
    staxids: str=None
    sscinames: str=None
    scomnames: str=None
    sblastname: str=None
    sskingdoms: str=None
    stitle: str=None
    salltitles: str=None
    sstrand: str=None
    qcovs: int=None
    qcovhsp: int=None

    def __repr__(self):
        dict_repr = ', '.join(
            f'{k}={repr(v)}'
            for k, v in filter(
                lambda item: item[1] is not None,
                self.__dict__.items()
            )
        )

        return f'{self.__class__.__name__}({dict_repr})'
    
    def __str__(self):
        return '\t'.join([str(v) for k, v in self.__dict__.items() if v is not None and k != "fields_used"])



    @classmethod
    def from_outfmt_str(cls, fmt_string: str, result_line: str=None):
        field_data = cls._get_field_data(fmt_string, result_line)
        return cls(**field_data)
    
    @staticmethod
    def _get_field_data(fmt_string: str, result_line: str):
        idx_flds = BlastResult._get_field_idxs(fmt_string)

        fld_data = {}
        fld_data["fields_used"] = set([v for v in idx_flds.values()])

        if result_line is not None:
            for n, datum in enumerate(result_line.split()):
                fld_data[idx_flds[n]] = datum
        
        return fld_data


    @staticmethod
    def _get_field_idxs(fmt_string: str):
        std = ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
               "qstart", "qend", "sstart", "send", "evalue", "bitscore"]
        duped = {
            "qseqid": False,
            "sseqid": False
        }
        
        flds_seen = set()
        idx_flds = {}
        idx = 0
        std_seen = False
        for fld in fmt_string.split():
            if fld == "std":
                if std_seen:
                    # can't have std twice
                    continue
                std_seen = True
                for std_fld in std:
                    if std_fld in flds_seen:
                        if std_fld not in duped:
                            # not going to be included in the std fields expansion
                            continue
                        if duped[std_fld]:
                            continue
                        idx_flds[idx] = std_fld
                        duped[std_fld] = True
                        idx += 1
                        continue

                    idx_flds[idx] = std_fld
                    flds_seen.add(std_fld)
                    idx += 1
                    continue
                continue
                    

            if fld in flds_seen:
                if fld not in duped:
                    # can't occur more than once
                    idx += 1
                    continue
                if duped[fld]:
                    continue
                idx_flds[idx] = fld
                flds_seen.add(fld)
                idx += 1
                continue
            
            idx_flds[idx] = fld
            flds_seen.add(fld)
            idx += 1
            continue
            
        return idx_flds


    def can_verify_perfect_match(self, qcov_hsp_perc: bool=False):
        # qcov_hsp_perc option filters hits to only include those where the whole query matched within a single HSP
        # If the match is also 100% identical over its length then it is a perfect match.
        # can achieve the same effect by including qcovhsp in outfmt
        if not qcov_hsp_perc and "qcovhsp" in self.fields_used:
            if self.qcovhsp == 100:
                qcov_hsp_perc = True
        if qcov_hsp_perc:
            no_mm_or_gap = any([
                "pident" in self.fields_used,
                "mismatch" in self.fields_used and any(
                    [i in self.fields_used for i in ["gapopen", "gaps"]]
                )
            ])
            if no_mm_or_gap:
                # If we have enough with just the qcov_hsp_perc plus outfmt fields
                return True
        
        # Otherwise need to check if fields in outfmt can do it without qcov_hsp_perc
        no_mm_or_gap = any([
            all([i in self.fields_used for i in ["length", "pident"]]),
            "nident" in self.fields_used,
            (
                all([i in self.fields_used for i in ["length", "mismatch"]]) 
                and any([i in self.fields_used for i in ["gapopen", "gaps"]])
            )
        ])
        full_length = "qlen" in self.fields_used

        return no_mm_or_gap and full_length
    

    def is_perfect_match(self, qcov_hsp_perc: bool=False) -> bool|None:
        """bool if knowable, None if unknowable"""
        if not self.can_verify_perfect_match(qcov_hsp_perc):
            return None
        
        # if qcovhsp used in outfmt, can replace command line argument version
        if not qcov_hsp_perc and "qcovhsp" in self.fields_used:
            if self.qcovhsp == 100:
                qcov_hsp_perc = True

        if qcov_hsp_perc:
            # determine available fields
            if "pident" in self.fields_used:
                return self.pident == 100
            
            # we must have mismatch. Which gap do we have?
            if "gapopen" in self.fields_used:
                return self.mismatch == 0 and self.gapopen == 0
            
            if "gaps" in self.fields_used:
                return self.mismatch == 0 and self.gaps == 0

        if "pident" in self.fields_used and "length" in self.fields_used:
                return self.pident == 100 and self.length == self.qlen
        
        if "nident" in self.fields_used:
            return self.nident == self.qlen
            
        # we must have mismatch. Which gap do we have?
        if "gapopen" in self.fields_used:
            return (
                self.mismatch == 0 
                and self.gapopen == 0
                and self.length == self.qlen
            )
        
        if "gaps" in self.fields_used:
            return (
                self.mismatch == 0 
                and self.gaps == 0
                and self.length == self.qlen
            )

class Seq():
    _rc = {
        "A": "T",
        "T": "A",
        "C": "G",
        "G": "C",
        "N": "N"
    }
    def __init__(self, header: str, seq: str):
        self.header = header
        self.seq = seq
    
    def reverse_complement(self) -> "Seq":
        revseq = [self._rc[b] for b in self.seq[::-1]]
        return Seq(self.header, revseq)

    def __eq__(self, other: "Seq") -> bool:
        if not isinstance(other, Seq):
            raise TypeError(f"== not supported between {self.__class__.__name__} and {other.__class__.__name__}")
        return self.seq == other.seq
    
    def __gt__(self, other: "Seq") -> bool:
        if not isinstance(other, Seq):
            raise TypeError(f"ordering not supported between {self.__class__.__name__} and {other.__class__.__name__}")
        return self.header > other.header
    
    def __ge__(self, other: "Seq") -> bool:
        if not isinstance(other, Seq):
            raise TypeError(f"ordering not supported between {self.__class__.__name__} and {other.__class__.__name__}")
        return self.header >= other.header
    
    def __lt__(self, other: "Seq") -> bool:
        if not isinstance(other, Seq):
            raise TypeError(f"ordering not supported between {self.__class__.__name__} and {other.__class__.__name__}")
        return self.header < other.header
    
    def __le__(self, other: "Seq") -> bool:
        if not isinstance(other, Seq):
            raise TypeError(f"ordering not supported between {self.__class__.__name__} and {other.__class__.__name__}")
        return self.header <= other.header

    def __str__(self) -> str:
        return f"{self.header}\n{self.seq}"

class FastaSeq():
    def __init__(self, seqs: list[Seq]=None):
        if seqs is None:
            self.seqs = []
        else:
            self.seqs = seqs
        
    @classmethod
    def from_fasta(cls, fasta_str: str):
        seqs = []
        if ">" not in fasta_str or "\n" not in fasta_str:
             return cls()
        
        for entry in fasta_str.split(">"):
            lines = [l for l in entry.split("\n") if l != ""]
            head = lines[0]
            seq = "".join(lines[1])
            seqs.append(Seq(head, seq))
        return cls(seqs)

    def __str__(self) -> str:
        return "\n".join(self.seqs)


def check_class_method(cls, meth):
    """Check class for a method and print a clear message if absent

    Args:
        meth (str): The method of which to assess the existence callable-ity
    """
    # Figure out if message should say a or an for this method
    a_an = "an" if meth[0] in {"a", "e", "i", "o" "u"} else "a"
    if not hasattr(cls, meth):
        raise(f"Your {cls.__name__} class does not have {a_an} {meth} method.")
    else:
        if not callable(eval(f"cls.{meth}")):
            raise(f"Your {cls.__name__} class does have {a_an} {meth} attribute, but it is not callable")


def check_class_attribute(cls, attr):
    """Check class for an attribute and print a clear message if absent

    Args:
        attr (str): The attribute of which to assess the existence
    """
    a_an = "an" if attr[0] in {"a", "e", "i", "o" "u"} else "a"
    if not hasattr(cls, attr):
        raise(f"Your {cls.__name__} class does not have {a_an} {attr} attribute.")


def check_attribute_value(instance, attr, expected, tested_data):
    """Compare an attribute of a class instance to an expected value

    Args:
        instance (Object): The instance you want to assess
        attr (str): The attribute whose value should be compared
        expected (any): The expected value
        tested_data (str): the nature of the tested data
    """
    a_an = "an" if tested_data[0] in {"a", "e", "i", "o", "u"} else "a"
    value = getattr(instance, attr)
    try:
        assert value == expected
    except:
        raise(f"Your {instance.__class__.__name__}.{attr} contains {value} for {a_an} {tested_data}, when it should have contained {expected}.")


def check_method_output(instance, method, expected, tested_data, args=(), kwargs=None):
    """Compare an attribute of a class instance to an expected value

    Args:
        instance (Object): The instance you want to assess
        method (str): The method whose return value should be compared
        args (tuple[any]): The arguments to provide to the method when called
        kwargs (dict[str, any]): The keyword arguments to provide to the method when called
        expected (any): The expected value
        tested_data (str): the nature of the tested data
    """
    if kwargs == None:
        kwargs = {}
    a_an = "an" if tested_data[0] in {"a", "e", "i", "o", "u"} else "a"
    try:
        value = eval(f"instance.{method}(*args, **kwargs)")
    except Exception as e:
        raise(f"Your {instance.__class__.__name__}.{method} for {a_an} {tested_data}, when it was run with input {args}. The error was {e}")
    try:
        assert value == expected
    except:
        raise(f"Your {instance.__class__.__name__}.{method} returned {repr(value)} for {a_an} {tested_data}, when it should have returned {repr(expected)}.")


def recursive_type_str(obj: object) -> str:
    def _is_container(obj: object) -> bool:
        """Check if it can contain elements but is not a string
        
        i.e., things like list, set, tuple, dict
        """
        return hasattr(obj, '__iter__') and hasattr(obj, '__contains__') and not isinstance(obj, str)

    def _traverse_type(obj: object) -> str:
        if _is_container(obj):
            obj_name = obj.__class__.__name__
            types = [_traverse_type(item) for item in obj]
            match obj_name:
                case "dict":
                    value_types = [_traverse_type(item) for item in obj.values()]
                    key_hint = "|".join(sorted(list(set(types))))
                    value_hint = "|".join(sorted(list(set(value_types))))
                    hint = f"{obj_name}[{key_hint},{value_hint}]"
                case "tuple":
                    hint = f"{obj_name}[{",".join(types)}]"
                case _:
                    hint = f"{obj_name}[{"|".join(sorted(list(set(types))))}]"
            return hint
        else:
            return obj.__class__.__name__
    
    return _traverse_type(obj)
