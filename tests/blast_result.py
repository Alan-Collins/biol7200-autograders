from dataclasses import field

from pydantic import BaseModel

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
        field_data["fields_used"] = set(field_data.keys())
        return cls(**field_data)
    
    @staticmethod
    def _get_field_data(fmt_string: str, result_line: str):
        idx_flds = BlastResult._get_field_idxs(fmt_string)

        fld_data = {}
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
