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
		final int n = b.length;
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
	
	/**
	 * // TODO: add test
	 * @param A m by n matrix (m,n>0)
	 * @return
	 */
	public static int[] nonZeroRows(final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
		if((m<=0)||(n<=0)) {
			throw new IllegalArgumentException("degenerate matrix");
		}
		final boolean[] sawNZ = new boolean[m];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]!=0) {
					sawNZ[i] = true;
				}
			}
		}
		int nnz = 0;
		for(int i=0;i<m;++i) {
			if(sawNZ[i]) {
				++nnz;
			}
		}
		final int[] nzRows = new int[nnz];
		nnz = 0;
		for(int i=0;i<m;++i) {
			if(sawNZ[i]) {
				nzRows[nnz] = i;
				++nnz;
			}
		}
		return nzRows;
	}
	
	// TODO: add test
	public static int[][] rowRestrict(final int[][] A, final int[] rows) {
		final int n = A[0].length;
		final int m2 = rows.length;
		final int[][] A2 = new int[m2][n];
		for(int i2=0;i2<m2;++i2) {
			final int i = rows[i2];
			for(int j=0;j<n;++j) {
				A2[i2][j] = A[i][j];
			}
		}
		return A2;
	}
	
	// TODO: add test
	public static int[][] colRestrict(final int[][] A, final int[] cols) {
		final int m = A.length;
		final int n2 = cols.length;
		final int[][] A2 = new int[m][n2];
		for(int i=0;i<m;++i) {
			for(int j2=0;j2<n2;++j2) {
				final int j = cols[j2];
				A2[i][j2] = A[i][j];
			}
		}
		return A2;
	}
}