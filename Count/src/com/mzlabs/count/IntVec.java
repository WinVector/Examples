package com.mzlabs.count;

import java.util.Arrays;


final class IntVec implements Comparable<IntVec> {
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
	
	public static int compare(final int[] x, final int[] y) {
		final int m = x.length;
		if(m!=y.length) {
			if(m>=y.length) {
				return 1;
			} else {
				return -1;
			}
		}
		for(int i=0;i<m;++i) {
			if(x[i]!=y[i]) {
				if(x[i]>=y[i]) {
					return 1;
				} else {
					return -1;
				}
			}
		}
		return 0;		
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
		return compare(b,o.b);
	}
	
	@Override
	public boolean equals(final Object o) {
		return compareTo((IntVec)o)==0;
	}
	
	@Override
	public int hashCode() {
		return hashCode;
	}
	
	public static String toString(final int[] x) {
		final StringBuilder bstr = new StringBuilder();
		boolean first = true;
		for(final int xi: x) {
			if(first) {
				first = false;
			} else {
				bstr.append(", ");
			}
			bstr.append(xi);
		}
		return bstr.toString();
	}
	
	@Override 
	public String toString() {
		return "[" + toString(b) + "]";
	}
}