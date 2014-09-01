package com.mzlabs.count;

import java.util.Arrays;

/**
 * faster integer linear operator for sparse matrices
 * @author johnmount
 *
 */
final class IntLinOp {
	private final int[] is;
	private final int[] js;
	private final int[] Aijs;
	
	public IntLinOp(final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
		int ci = 0;
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]!=0) {
					++ci;
				}
			}
		}
		final int nnz = ci;
		is = new int[nnz];
		js = new int[nnz];
		Aijs = new int[nnz];
		ci = 0;
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]!=0) {
					is[ci] = i;
					js[ci] = j;
					Aijs[ci] = A[i][j];
					++ci;
				}
			}
		}

	}

	/**
	 * place A x into r
	 * @param x n vector
	 * @param r m vector
	 */
	public void mult(final int[] x, final int[] r) {
		Arrays.fill(r,0);
		final int nnz = is.length;
		for(int ci=0;ci<nnz;++ci) {
			final int i = is[ci];
			final int j = js[ci];
			final int Aij = Aijs[ci];
			r[i] += Aij*x[j];
		}
	}
	
	/**
	 * place A x into r
	 * @param A m by n matrix
	 * @param x n vector
	 * @param r m vector
	 */
	public static void mult(final int[][] A, final int[] x, final int[] r) {
		Arrays.fill(r,0);
		final int m = A.length;
		final int n = A[0].length;
		for(int i=0;i<m;++i) {
			int ri = 0;
			for(int j=0;j<n;++j) {
				ri += A[i][j]*x[j];
			}
			r[i] = ri;
		}
	}

}
