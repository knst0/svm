# -*- coding: utf-8 -*-
# Pure-Python XNB (LZX) -> dict unpacker for Stardew Valley Dictionary[string,string] assets.
# LZX port of MonoGame's LzxDecoder.cs (derived from libmspack, (C) Stuart Caie / Ali Scissons).
import struct, io, sys, json, os

# ---------- LZX constants ----------
MIN_MATCH=2; NUM_CHARS=256
PRETREE_NUM_ELEMENTS=20; ALIGNED_NUM_ELEMENTS=8
NUM_PRIMARY_LENGTHS=7; NUM_SECONDARY_LENGTHS=249
PRETREE_MAXSYMBOLS=20; PRETREE_TABLEBITS=6
MAINTREE_MAXSYMBOLS=NUM_CHARS+50*8; MAINTREE_TABLEBITS=12
LENGTH_MAXSYMBOLS=NUM_SECONDARY_LENGTHS+1; LENGTH_TABLEBITS=12
ALIGNED_MAXSYMBOLS=8; ALIGNED_TABLEBITS=7
LENTABLE_SAFETY=64
BT_INVALID=0; BT_VERBATIM=1; BT_ALIGNED=2; BT_UNCOMPRESSED=3
M32=0xFFFFFFFF

class BitBuf:
    __slots__=("buf","left","s")
    def __init__(self,s): self.s=s; self.buf=0; self.left=0
    def init(self): self.buf=0; self.left=0
    def _rb(self):
        b=self.s.read(1)
        return b[0] if b else 0xFF
    def ensure(self,bits):
        while self.left<bits:
            lo=self._rb(); hi=self._rb()
            self.buf|=((hi<<8)|lo)<<(16-self.left)
            self.buf&=M32
            self.left+=16
    def peek(self,bits): return (self.buf>>(32-bits))&M32
    def remove(self,bits): self.buf=(self.buf<<bits)&M32; self.left-=bits
    def read(self,bits):
        if bits<=0: return 0
        self.ensure(bits); r=self.peek(bits); self.remove(bits); return r

class Lzx:
    def __init__(self, window=16):
        wnd=1<<window
        self.window=bytearray([0xDC])*wnd
        self.window_size=wnd; self.window_posn=0
        self.R0=self.R1=self.R2=1
        self.extra_bits=[0]*52
        j=0
        for i in range(0,51,2):
            self.extra_bits[i]=self.extra_bits[i+1]=j
            if i!=0 and j<17: j+=1
        self.position_base=[0]*51
        j=0
        for i in range(0,51):
            self.position_base[i]=j; j+=1<<self.extra_bits[i]
        posn_slots=window<<1
        self.main_elements=NUM_CHARS+(posn_slots<<3)
        self.header_read=0
        self.block_type=BT_INVALID
        self.block_remaining=0; self.block_length=0
        self.intel_filesize=0; self.intel_started=0
        self.PRETREE_table=[0]*((1<<PRETREE_TABLEBITS)+(PRETREE_MAXSYMBOLS<<1))
        self.PRETREE_len=[0]*(PRETREE_MAXSYMBOLS+LENTABLE_SAFETY)
        self.MAINTREE_table=[0]*((1<<MAINTREE_TABLEBITS)+(MAINTREE_MAXSYMBOLS<<1))
        self.MAINTREE_len=[0]*(MAINTREE_MAXSYMBOLS+LENTABLE_SAFETY)
        self.LENGTH_table=[0]*((1<<LENGTH_TABLEBITS)+(LENGTH_MAXSYMBOLS<<1))
        self.LENGTH_len=[0]*(LENGTH_MAXSYMBOLS+LENTABLE_SAFETY)
        self.ALIGNED_table=[0]*((1<<ALIGNED_TABLEBITS)+(ALIGNED_MAXSYMBOLS<<1))
        self.ALIGNED_len=[0]*(ALIGNED_MAXSYMBOLS+LENTABLE_SAFETY)

    def make_table(self,nsyms,nbits,length,table):
        bit_num=1; pos=0
        table_mask=1<<nbits; bit_mask=table_mask>>1; next_symbol=bit_mask
        while bit_num<=nbits:
            for sym in range(nsyms):
                if length[sym]==bit_num:
                    leaf=pos
                    pos+=bit_mask
                    if pos>table_mask: return 1
                    fill=bit_mask
                    while fill>0:
                        table[leaf]=sym; leaf+=1; fill-=1
            bit_mask>>=1; bit_num+=1
        if pos!=table_mask:
            for sym in range(pos,table_mask): table[sym]=0
            pos<<=16; table_mask<<=16; bit_mask=1<<15
            while bit_num<=16:
                for sym in range(nsyms):
                    if length[sym]==bit_num:
                        leaf=pos>>16
                        for fill in range(bit_num-nbits):
                            if table[leaf]==0:
                                table[next_symbol<<1]=0; table[(next_symbol<<1)+1]=0
                                table[leaf]=next_symbol; next_symbol+=1
                            leaf=table[leaf]<<1
                            if (pos>>(15-fill))&1: leaf+=1
                        table[leaf]=sym
                        pos+=bit_mask
                        if pos>table_mask: return 1
                bit_mask>>=1; bit_num+=1
        if pos==table_mask: return 0
        for sym in range(nsyms):
            if length[sym]!=0: return 1
        return 0

    def read_huff(self,table,lengths,nsyms,nbits,bb):
        bb.ensure(16)
        i=table[bb.peek(nbits)]
        if i>=nsyms:
            j=1<<(32-nbits)
            while True:
                j>>=1; i=(i<<1)
                if bb.buf & j: i|=1
                if j==0: return 0
                i=table[i]
                if i<nsyms: break
        j=lengths[i]; bb.remove(j); return i

    def read_lengths(self,lens,first,last,bb):
        for x in range(20):
            self.PRETREE_len[x]=bb.read(4)
        self.make_table(PRETREE_MAXSYMBOLS,PRETREE_TABLEBITS,self.PRETREE_len,self.PRETREE_table)
        x=first
        while x<last:
            z=self.read_huff(self.PRETREE_table,self.PRETREE_len,PRETREE_MAXSYMBOLS,PRETREE_TABLEBITS,bb)
            if z==17:
                y=bb.read(4)+4
                while y>0: lens[x]=0; x+=1; y-=1
            elif z==18:
                y=bb.read(5)+20
                while y>0: lens[x]=0; x+=1; y-=1
            elif z==19:
                y=bb.read(1)+4
                z=self.read_huff(self.PRETREE_table,self.PRETREE_len,PRETREE_MAXSYMBOLS,PRETREE_TABLEBITS,bb)
                z=lens[x]-z
                if z<0: z+=17
                while y>0: lens[x]=z; x+=1; y-=1
            else:
                z=lens[x]-z
                if z<0: z+=17
                lens[x]=z; x+=1

    def decompress(self,inData,inLen,outData,outLen):
        bb=BitBuf(inData); startpos=inData.tell()
        window=self.window; window_posn=self.window_posn; window_size=self.window_size
        R0,R1,R2=self.R0,self.R1,self.R2
        bb.init()
        if self.header_read==0:
            intel=bb.read(1)
            if intel!=0:
                i=bb.read(16); j=bb.read(16); self.intel_filesize=((i<<16)|j)
            self.header_read=1
        togo=outLen
        while togo>0:
            if self.block_remaining==0:
                if self.block_type==BT_UNCOMPRESSED:
                    if (self.block_length & 1)==1: inData.read(1)
                    bb.init()
                self.block_type=bb.read(3)
                i=bb.read(16); j=bb.read(8)
                self.block_remaining=self.block_length=((i<<8)|j)
                bt=self.block_type
                if bt==BT_ALIGNED:
                    for i in range(8): self.ALIGNED_len[i]=bb.read(3)
                    self.make_table(ALIGNED_MAXSYMBOLS,ALIGNED_TABLEBITS,self.ALIGNED_len,self.ALIGNED_table)
                    self._read_main(bb)
                elif bt==BT_VERBATIM:
                    self._read_main(bb)
                elif bt==BT_UNCOMPRESSED:
                    self.intel_started=1
                    bb.ensure(16)
                    if bb.left>16: inData.seek(-2,1)
                    def r4():
                        lo=inData.read(1)[0]; ml=inData.read(1)[0]; mh=inData.read(1)[0]; hi=inData.read(1)[0]
                        return lo|(ml<<8)|(mh<<16)|(hi<<24)
                    R0=r4(); R1=r4(); R2=r4()
                else:
                    raise ValueError("bad block type %d"%bt)
            while True:
                this_run=self.block_remaining
                if this_run<=0 or togo<=0: break
                if this_run>togo: this_run=togo
                togo-=this_run; self.block_remaining-=this_run
                window_posn&=window_size-1
                if window_posn+this_run>window_size: raise ValueError("window overrun")
                bt=self.block_type
                if bt==BT_VERBATIM or bt==BT_ALIGNED:
                    aligned = (bt==BT_ALIGNED)
                    while this_run>0:
                        me=self.read_huff(self.MAINTREE_table,self.MAINTREE_len,MAINTREE_MAXSYMBOLS,MAINTREE_TABLEBITS,bb)
                        if me<NUM_CHARS:
                            window[window_posn]=me; window_posn+=1; this_run-=1
                        else:
                            me-=NUM_CHARS
                            match_length=me & NUM_PRIMARY_LENGTHS
                            if match_length==NUM_PRIMARY_LENGTHS:
                                lf=self.read_huff(self.LENGTH_table,self.LENGTH_len,LENGTH_MAXSYMBOLS,LENGTH_TABLEBITS,bb)
                                match_length+=lf
                            match_length+=MIN_MATCH
                            match_offset=me>>3
                            if not aligned:
                                if match_offset>2:
                                    if match_offset!=3:
                                        extra=self.extra_bits[match_offset]
                                        vb=bb.read(extra)
                                        match_offset=self.position_base[match_offset]-2+vb
                                    else:
                                        match_offset=1
                                    R2=R1; R1=R0; R0=match_offset
                                elif match_offset==0: match_offset=R0
                                elif match_offset==1: match_offset=R1; R1=R0; R0=match_offset
                                else: match_offset=R2; R2=R0; R0=match_offset
                            else:
                                if match_offset>2:
                                    extra=self.extra_bits[match_offset]
                                    match_offset=self.position_base[match_offset]-2
                                    if extra>3:
                                        extra-=3; vb=bb.read(extra); match_offset+=(vb<<3)
                                        ab=self.read_huff(self.ALIGNED_table,self.ALIGNED_len,ALIGNED_MAXSYMBOLS,ALIGNED_TABLEBITS,bb)
                                        match_offset+=ab
                                    elif extra==3:
                                        ab=self.read_huff(self.ALIGNED_table,self.ALIGNED_len,ALIGNED_MAXSYMBOLS,ALIGNED_TABLEBITS,bb)
                                        match_offset+=ab
                                    elif extra>0:
                                        vb=bb.read(extra); match_offset+=vb
                                    else:
                                        match_offset=1
                                    R2=R1; R1=R0; R0=match_offset
                                elif match_offset==0: match_offset=R0
                                elif match_offset==1: match_offset=R1; R1=R0; R0=match_offset
                                else: match_offset=R2; R2=R0; R0=match_offset
                            rundest=window_posn; this_run-=match_length
                            if window_posn>=match_offset:
                                runsrc=rundest-match_offset
                            else:
                                runsrc=rundest+(window_size-match_offset)
                                copy_length=match_offset-window_posn
                                if copy_length<match_length:
                                    match_length-=copy_length; window_posn+=copy_length
                                    while copy_length>0:
                                        window[rundest]=window[runsrc]; rundest+=1; runsrc+=1; copy_length-=1
                                    runsrc=0
                            window_posn+=match_length
                            while match_length>0:
                                window[rundest]=window[runsrc]; rundest+=1; runsrc+=1; match_length-=1
                elif bt==BT_UNCOMPRESSED:
                    buf=inData.read(this_run)
                    window[window_posn:window_posn+this_run]=buf
                    window_posn+=this_run
                else:
                    raise ValueError("bad block type")
        swp=window_posn
        if swp==0: swp=window_size
        swp-=outLen
        outData.write(bytes(window[swp:swp+outLen]))
        self.window_posn=window_posn; self.R0=R0; self.R1=R1; self.R2=R2

    def _read_main(self,bb):
        self.read_lengths(self.MAINTREE_len,0,256,bb)
        self.read_lengths(self.MAINTREE_len,256,self.main_elements,bb)
        self.make_table(MAINTREE_MAXSYMBOLS,MAINTREE_TABLEBITS,self.MAINTREE_len,self.MAINTREE_table)
        if self.MAINTREE_len[0xE8]!=0: self.intel_started=1
        self.read_lengths(self.LENGTH_len,0,NUM_SECONDARY_LENGTHS,bb)
        self.make_table(LENGTH_MAXSYMBOLS,LENGTH_TABLEBITS,self.LENGTH_len,self.LENGTH_table)

# ---------- XNB container ----------
def lzx_frames(comp, decomp_size):
    s=io.BytesIO(comp); out=io.BytesIO(); dec=Lzx(16); pos=0; n=len(comp)
    while pos<n:
        s.seek(pos)
        hi=s.read(1)[0]; lo=s.read(1)[0]
        block_size=(hi<<8)|lo; frame_size=0x8000
        if hi==0xFF:
            hi=lo; lo=s.read(1)[0]; frame_size=(hi<<8)|lo
            hi=s.read(1)[0]; lo=s.read(1)[0]; block_size=(hi<<8)|lo
            pos+=5
        else:
            pos+=2
        if block_size==0 or frame_size==0: break
        s.seek(pos)
        dec.decompress(s,block_size,out,frame_size)
        pos+=block_size
        if out.tell()>=decomp_size: break
    return out.getvalue()[:decomp_size]

def decompress_xnb(path):
    data=open(path,'rb').read()
    assert data[:3]==b'XNB', "not XNB: "+path
    flags=data[5]
    file_size=struct.unpack_from('<I',data,6)[0]
    if flags & 0x80:
        decomp_size=struct.unpack_from('<I',data,10)[0]
        comp=data[14:file_size]
        return lzx_frames(comp,decomp_size)
    elif flags & 0x40:
        raise NotImplementedError("LZ4 not supported")
    else:
        return data[10:file_size]

def read7(b,pos):
    res=0; sh=0
    while True:
        x=b[pos]; pos+=1; res|=(x&0x7F)<<sh
        if not (x&0x80): break
        sh+=7
    return res,pos

def parse_dict(path):
    body=decompress_xnb(path); pos=0
    nr,pos=read7(body,pos)
    readers=[]
    for _ in range(nr):
        sl,pos=read7(body,pos); name=body[pos:pos+sl].decode('utf-8','replace'); pos+=sl
        pos+=4
        readers.append(name)
    nshared,pos=read7(body,pos)
    tid,pos=read7(body,pos)
    count=struct.unpack_from('<i',body,pos)[0]; pos+=4
    def rstr(p):
        oid,p=read7(body,p)
        if oid==0: return None,p
        sl,p=read7(body,p); s=body[p:p+sl].decode('utf-8'); p+=sl
        return s,p
    d={}
    for _ in range(count):
        k,pos=rstr(pos)
        v,pos=rstr(pos)
        d[k]=v
    return d, readers

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Unpack a Stardew Valley Dictionary[string,string] .xnb (LZX) to JSON.")
    ap.add_argument("input", help="path to a .xnb file (e.g. Characters/Dialogue/Shane.ru-RU.xnb)")
    ap.add_argument("-o", "--output", help="write JSON here (default: print to stdout)")
    args = ap.parse_args()
    d, readers = parse_dict(args.input)
    sys.stderr.write("readers: %s\nentries: %d\n" % (readers, len(d)))
    text = json.dumps(d, ensure_ascii=False, indent=1)
    if args.output:
        open(args.output, "w", encoding="utf-8").write(text)
        sys.stderr.write("wrote %s\n" % args.output)
    else:
        sys.stdout.write(text + "\n")
