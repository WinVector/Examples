package com.mzlabs.count.util;

import java.util.Arrays;
import java.util.SortedMap;
import java.util.TreeMap;

import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;

public final class IntMat implements Comparable<IntMat> {
	private final int hashCode;
	private final int[][] A;
	
	public IntMat(final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
		this.A = new int[m][];
		int hc = 0;
		for(int i=0;i<m;++i) {
			this.A[i] = Arrays.copyOf(A[i],n);
			hc += Arrays.hashCode(A[i]);
		}
		hashCode = hc;
	}

	@Override
	public int compareTo(final IntMat o) {
		if(hashCode!=o.hashCode) {
			if(hashCode>=o.hashCode) { 
				return 1;
			} else {
				return -1;
			}
		}
		final int m = A.length;
		if(m!=o.A.length) {
			if(m>=o.A.length) {
				return 1;
			} else {
				return -1;
			}
		}
		final int n = A[0].length;
		if(n!=o.A[0].length) {
			if(n>=o.A[0].length) {
				return 1;
			} else {
				return -1;
			}
		}
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]!=o.A[i][j]) {
					if(A[i][j]>=o.A[i][j]) {
						return 1;
					} else {
						return -1;
					}
				}
			}
		}
		return 0;
	}
	
	@Override
	public boolean equals(final Object o) {
		return compareTo((IntMat)o)==0;
	}
	
	@Override
	public int hashCode() {
		return hashCode;
	}

	public static final class RowDescription {
		public final int origIndex;  
		public final int newIndex; // -1 for all non-primary rows
		public double[] soln = null;
		
		public RowDescription(final int origIndex, 
				final int newIndex, final double[] soln) {
			this.origIndex = origIndex;
			this.newIndex = newIndex;
			this.soln = soln;
		}
		
		@Override
		public String toString() {
			return "(" + origIndex + ":" + newIndex + ")";
		}
	}
	
	public static RowDescription[] buildMapToCannon(final int[][] A) {
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		final int m = A.length;
		final int n = A[0].length;
		final SortedMap<Integer,Integer> orderingMap = new TreeMap<Integer,Integer>();
		final int[] rowBasis = IntMat.rowBasis(A);
		for(final int i: rowBasis) {
			orderingMap.put(i,orderingMap.size());
		}
		final int n2 = rowBasis.length;
		final ColtMatrix mat = factory.newMatrix(n,n2, false);
		for(int j=0;j<n;++j) {
			for(int jj=0;jj<n2;++jj) {
				mat.set(j,jj,A[rowBasis[jj]][j]);
			}
		}
		final RowDescription[] descr = new RowDescription[m];
		for(int i=0;i<m;++i) {
			final Integer newIndex = orderingMap.get(i);
			if(null!=newIndex) {
				descr[i] = new RowDescription(i,newIndex,null);
			} else {
				final double[] v = new double[n];
				for(int j=0;j<n;++j) {
					v[j] = A[i][j];
				}
				final double[] soln = mat.solve(v);
				final double[] expandedSoln = new double[m];
				for(int ii=0;ii<rowBasis.length;++ii) {
					expandedSoln[rowBasis[ii]] = soln[ii];
				}
				descr[i] = new RowDescription(i,-1,expandedSoln);
			}
		}
		return descr;
	}
	
	public static int[] mapVector(final RowDescription[] rowDescr, final int[] b) {
		int m2 = 0;
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				++m2;
			}
		}
		final int[] b2 = new int[m2];
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				b2[di.newIndex] = b[di.origIndex];
			}
		}
		return b2;
	}
	
	/**
	 * pullBack(rowDescr,mapVector(rowDescr,x)) == x // TODO: add test
	 * @param rowDescr
	 * @param b
	 * @return
	 */
	public static int[] pullBackVector(final RowDescription[] rowDescr, final int[] b) {
		final int n = rowDescr.length;
		final int[] x = new int[n];
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				x[di.origIndex] = b[di.newIndex];
			}
		}
		for(final RowDescription di: rowDescr) {
			if(di.newIndex<0) {
				double sum = 0;
				for(int j=0;j<n;++j) {
					sum += di.soln[j]*x[j];
				}
				x[di.origIndex] = (int)Math.round(sum);
			}
		}
		return x;
	}
	
	public static boolean checkImpliedEntries(final RowDescription[] rowDescr, final int[] b) {
		for(final RowDescription di: rowDescr) {
			if(di.newIndex<0) {
				double check = 0.0;
				final int m = di.soln.length;
				if(m!=b.length) {
					return false;
				}
				for(int i=0;i<m;++i) {
					check += b[i]*di.soln[i];
				}
				if(Math.abs(check-b[di.origIndex])>1.e-5) {
					return false;
				}
			}
		}
		return true;
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
	public static int[][] rowRestrict(final int[][] A, final RowDescription[] rowDescr) {
		int m2 = 0;
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				++m2;
			}
		}
		final int n = A[0].length;
		final int[][] A2 = new int[m2][];
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				A2[di.newIndex] = Arrays.copyOf(A[di.origIndex],n);
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
	
	// TODO: add test
	public static int[] rowBasis(final int[][] A) {
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		final int m = A.length;
		final int n = A[0].length;
		ColtMatrix mat = factory.newMatrix(n, m, false);
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				mat.set(j,i,A[i][j]);
			}
		}
		return mat.columnMatrix().colBasis(null, 1.0e-8);
	}
}
