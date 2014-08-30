package com.mzlabs.count;

import java.util.Arrays;


public final class IntVec implements Comparable<IntVec> {
	private final int hashCode;
	private final int[] b;
	
	public IntVec(final int[] b) {
		hashCode = Arrays.hashCode(b);
		this.b = Arrays.copyOf(b,b.length);
	}

	public boolean isZero() {
		for(final int bi: b) {
			if(bi>0) {
				return false;
			}
		}
		return true;
	}
	
	public final int dim() {
		return b.length;
	}
	
	public final int get(final int i) {
		return b[i];
	}
	
	@Override
	public int compareTo(final IntVec o) {
		if(hashCode!=o.hashCode) {
			if(hashCode>=o.hashCode) {
				return 1;
			} else {
				return -1;
			}
		}	
		final int m = b.length;
		if(m!=o.b.length) {
			if(m>=o.b.length) {
				return 1;
			} else {
				return -1;
			}
		}
		for(int i=0;i<m;++i) {
			if(b[i]!=o.b[i]) {
				if(b[i]>=o.b[i]) {
					return 1;
				} else {
					return -1;
				}
			}
		}
		return 0;
	}
	
	@Override
	public boolean equals(final Object o) {
		return compareTo((IntVec)o)==0;
	}
	
	@Override
	public int hashCode() {
		return hashCode;
	}
	
	@Override 
	public String toString() {
		final StringBuilder bstr = new StringBuilder();
		bstr.append("{ ");
		for(final int bi: b) {
			bstr.append(bi);
			bstr.append(" ");
		}
		bstr.append("}");
		return bstr.toString();
	}
}