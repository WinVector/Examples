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
	
	
	public double[] asDouble() {
		final int m = b.length;
		final double[] x = new double[m];
		for(int i=0;i<m;++i) {
			x[i] = b[i];
		}
		return x;
	}
	
	/**
	 * advance a non-negative through all non-negative combinations less than bound, (starting at all zeros)
	 * @param bvec
	 * @return true if we haven't wrapped around to all zeros
	 */
	public static boolean advanceLT(final int bound, final int[] bvec) {
		final int n = bvec.length;
		final int boundMinus1 = bound-1;
		// look for right-most advancable item
		for(int i=n-1;i>=0;--i) {
			if(bvec[i]<boundMinus1) {
				bvec[i] += 1;
				return true;
			}
			bvec[i] = 0;
		}
		return false;
	}

	/**
	 * advance a non-negative through all non-negative combinations less than equal to bound, (starting at all zeros)
	 * @param bvec
	 * @return true if we haven't wrapped around to all zeros
	 */
	public boolean advanceLE(final int[] bvec) {
		final int n = bvec.length;
		// look for right-most incrementable item
		for(int i=n-1;i>=0;--i) {
			if(bvec[i]<get(i)) {
				bvec[i] += 1;
				return true;
			}
			bvec[i] = 0;
		}
		return false;
	}
}