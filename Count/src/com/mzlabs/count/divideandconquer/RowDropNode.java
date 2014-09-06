package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.Set;

import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.ZeroOneCounter;

final class RowDropNode implements NonNegativeIntegralCounter {
	private final int[][] A;
	private final int[] nzRows;
	private final int[] zRows;
	private final NonNegativeIntegralCounter underlying;
	
	RowDropNode(final int[][] A, final int[] nzRows, final NonNegativeIntegralCounter underlying) {
		this.A = A;
		this.nzRows = nzRows;
		this.underlying = underlying;
		final int m = A.length;
		final Set<Integer> droppedRows = new HashSet<Integer>();
		for(int i=0;i<m;++i) {
			droppedRows.add(i);
		}
		for(final int i: nzRows) {
			droppedRows.remove(i);
		}
		this.zRows = new int[droppedRows.size()];
		int i = 0;
		for(final Integer di: droppedRows) {
			this.zRows[i] = di;
			++i;
		}
	}
	
	
	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		for(final int i: zRows) {
			if(b[i]!=0) {
				final BigInteger count = BigInteger.ZERO;
				if(DivideAndConquerCounter.debug) {
					final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
					if(check.compareTo(count)!=0) {
						throw new IllegalStateException("got wrong answer");
					}
				}
				return count;
			}
		}
		final int m2 = nzRows.length;
		final int[] b2 = new int[m2];
		for(int i2=0;i2<m2;++i2) {
			final int i = nzRows[i2];
			b2[i2] = b[i];
		}
		final BigInteger count = underlying.countNonNegativeSolutions(b2);
		if(DivideAndConquerCounter.debug) {
			final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
			if(check.compareTo(count)!=0) {
				throw new IllegalStateException("got wrong answer");
			}
		}
		return count;
	}
	
	
	/**
	 * 
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
}
